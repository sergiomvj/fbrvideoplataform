from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from application.security.auth import CurrentUser
from application.services.structuring.engine import StructuringEngine
from application.services.visual_planning.engine import BriefPlanningEngine
from application.events.domain_events import (
    DomainEvent,
    EventBus,
    PRODUCTION_CREATED,
    PRODUCTION_STRUCTURED,
    PRODUCTION_VISUAL_PLANNED,
    PRODUCTION_MEDIA_SOURCED,
    PRODUCTION_HUMAN_REVIEW_REQUIRED,
    PRODUCTION_RENDER_COMPLETED,
    PRODUCTION_RENDER_FAILED,
    PRODUCTION_FAILED,
)
from integrations.openclaw.hooks import send_to_openclaw
from integrations.fbr_click.notifier import NotificationMapper
from api.schemas.productions import (
    ProductionIntakeRequest,
    ProductionResponse,
    StateTransitionResponse,
)
from api.schemas.production_detail import (
    CompositionSlotResponse,
    CompositionSummaryResponse,
    ProductionDetailResponse,
    RenderJobSummaryResponse,
    StateHistoryEntry,
)
from domain.composition.models import CompositionTimeline
from domain.render.models import RenderJob
from api.schemas.manual_binding import (
    ManualBindingCreateRequest,
    ManualBindingResponse,
)
from application.errors import AppError
from domain.production import (
    Production,
    ProductionMode,
    TemplateType,
    TemplateSelection,
    WorkflowState,
)
from domain.structuring.errors import StructuringError
from domain.visual_planning.errors import BriefPlanningError
from domain.templates import get_template
from domain.human_review.bindings import AssetBinding, AssetBindingStatus, BindingType
from application.services.manual_binding.service import manual_binding_service
from infrastructure.db.session import async_session
from infrastructure.db.production_repository import ProductionRepository
from infrastructure.db.composition_repository import CompositionRepository
from infrastructure.db.render_repository import RenderRepository
from infrastructure.db.narrative_repository import NarrativeRepository
from infrastructure.db.visual_brief_repository import VisualBriefRepository
from uuid import UUID, uuid4
from datetime import datetime

router = APIRouter(prefix="/productions", tags=["productions"])

_event_bus = EventBus()
_notification_mapper = NotificationMapper()

_event_bus.subscribe(PRODUCTION_HUMAN_REVIEW_REQUIRED, send_to_openclaw)
_event_bus.subscribe(PRODUCTION_RENDER_COMPLETED, send_to_openclaw)
_event_bus.subscribe(PRODUCTION_RENDER_FAILED, send_to_openclaw)
_event_bus.subscribe(PRODUCTION_FAILED, send_to_openclaw)


class EmitEventRequest(BaseModel):
    event_type: str
    payload: dict = {}


def _get_repo(session: AsyncSession) -> ProductionRepository:
    return ProductionRepository(session)


def _parse_production_id(production_id: str) -> UUID:
    try:
        return UUID(production_id)
    except (ValueError, AttributeError):
        raise AppError(message="Production not found", status_code=404)


async def _load_production(
    production_id: str, user_id: str, session: AsyncSession
) -> Production:
    pid = _parse_production_id(production_id)
    repo = _get_repo(session)
    production = await repo.get_by_id(pid)
    if not production:
        raise AppError(message="Production not found", status_code=404)
    if production.operator_user_id != user_id:
        raise AppError(message="Production not found", status_code=404)
    return production


@router.get("/")
async def list_productions(
    user: CurrentUser,
    session: AsyncSession = Depends(async_session),
) -> dict:
    repo = _get_repo(session)
    user_productions = await repo.list_by_operator(user.user_id)
    return {
        "productions": [_to_production_response(p) for p in user_productions],
        "count": len(user_productions),
    }


@router.post("/", response_model=ProductionResponse, status_code=201)
async def create_production(
    request: ProductionIntakeRequest,
    user: CurrentUser,
    session: AsyncSession = Depends(async_session),
) -> ProductionResponse:
    template = get_template(request.template_type_id)
    if not template:
        raise AppError(message="Invalid template", status_code=400)

    if not template.validate_variation(request.variation_id):
        raise AppError(
            message=f"Invalid variation '{request.variation_id}' for template '{request.template_type_id}'",
            status_code=400,
        )

    try:
        mode = ProductionMode(request.mode)
    except ValueError:
        raise AppError(
            message=f"Invalid mode '{request.mode}'. Must be 'automatic' or 'manual'",
            status_code=400,
        )

    if not template.validate_mode(mode):
        raise AppError(
            message=f"Mode '{request.mode}' is not compatible with template '{request.template_type_id}'",
            status_code=400,
        )

    template_selection = TemplateSelection(
        template_type=TemplateType(request.template_type_id),
        variation_id=request.variation_id,
    )

    production = Production(
        mode=mode,
        template_selection=template_selection,
        title=request.title,
        base_content=request.base_content,
        editorial_context=request.editorial_context,
        restrictions=request.restrictions,
        operator_user_id=user.user_id,
        organization_id=user.organization_id,
    )

    repo = _get_repo(session)
    await repo.save(production)

    event = DomainEvent(
        event_type=PRODUCTION_CREATED,
        production_id=production.id,
        payload={"title": production.title, "mode": production.mode.value},
        source="productions_route",
    )
    await _event_bus.emit(event)

    return _to_production_response(production)


@router.get("/{production_id}", response_model=ProductionDetailResponse)
async def get_production(
    production_id: str,
    user: CurrentUser,
    session: AsyncSession = Depends(async_session),
) -> ProductionDetailResponse:
    production = await _load_production(production_id, user.user_id, session)

    comp_repo = CompositionRepository(session)
    render_repo = RenderRepository(session)
    narr_repo = NarrativeRepository(session)
    brief_repo = VisualBriefRepository(session)

    composition = await comp_repo.get_by_production(production.id)
    render_job = await render_repo.get_by_production(production.id)
    narrative = await narr_repo.get_narrative(production.id)
    briefs = await brief_repo.get_briefs_by_production(production.id)

    return _to_production_detail_response(production, composition, render_job, narrative, briefs)


@router.post("/{production_id}/structure")
async def structure_production(
    production_id: str,
    user: CurrentUser,
    session: AsyncSession = Depends(async_session),
) -> dict:
    production = await _load_production(production_id, user.user_id, session)

    if production.current_state != WorkflowState.INTAKE:
        raise AppError(
            message=f"Production must be in INTAKE state to structure, current: {production.current_state.value}",
            status_code=400,
        )

    engine = StructuringEngine()
    try:
        narrative = await engine.structure(production)
    except StructuringError as e:
        raise AppError(message=e.message, status_code=422)

    production.transition_to(
        WorkflowState.STRUCTURING,
        reason="Structuring started",
        triggered_by=user.user_id,
    )

    await _event_bus.emit(
        DomainEvent(
            event_type=PRODUCTION_STRUCTURED,
            production_id=production.id,
            payload={"triggered_by": user.user_id},
            source="productions_route",
        )
    )

    production.transition_to(
        WorkflowState.VISUAL_PLANNING,
        reason="Structuring completed",
        triggered_by=user.user_id,
    )

    # Persist the structured narrative
    narr_repo = NarrativeRepository(session)
    await narr_repo.save_narrative(production, narrative)

    repo = _get_repo(session)
    await repo.save(production)

    return {
        "production_id": str(narrative.production_id),
        "template_type_id": narrative.template_type_id,
        "variation_id": narrative.variation_id,
        "objective": narrative.objective,
        "target_duration_seconds": narrative.target_duration_seconds,
        "total_duration": narrative.total_duration,
        "blocks": [
            {
                "id": str(b.id),
                "role": b.role.value,
                "text": b.text,
                "estimated_duration_seconds": b.estimated_duration_seconds,
                "scene_index": b.scene_index,
            }
            for b in narrative.blocks
        ],
    }


@router.post("/{production_id}/plan-visual")
async def plan_visual(
    production_id: str,
    user: CurrentUser,
    session: AsyncSession = Depends(async_session),
) -> dict:
    production = await _load_production(production_id, user.user_id, session)

    if production.current_state != WorkflowState.VISUAL_PLANNING:
        raise AppError(
            message=f"Production must be in VISUAL_PLANNING state, current: {production.current_state.value}",
            status_code=400,
        )

    # Load persisted narrative - must exist from prior structuring step
    narr_repo = NarrativeRepository(session)
    narrative = await narr_repo.get_narrative(production.id)

    if not narrative:
        raise AppError(
            message="No structured narrative found. Run /structure first.",
            status_code=400,
        )

    template = get_template(narrative.template_type_id)
    if not template:
        raise AppError(message="Template not found", status_code=400)

    planning_engine = BriefPlanningEngine()
    try:
        brief_set = await planning_engine.generate_briefs(narrative, template)
    except BriefPlanningError as e:
        raise AppError(message=e.message, status_code=422)

    production.transition_to(
        WorkflowState.MEDIA_SOURCING,
        reason="Visual planning completed",
        triggered_by=user.user_id,
    )

    # Persist the visual briefs
    brief_repo = VisualBriefRepository(session)
    await brief_repo.save_briefs(production, brief_set.briefs)

    await _event_bus.emit(
        DomainEvent(
            event_type=PRODUCTION_VISUAL_PLANNED,
            production_id=production.id,
            payload={"triggered_by": user.user_id},
            source="productions_route",
        )
    )

    repo = _get_repo(session)
    await repo.save(production)

    return {
        "production_id": str(brief_set.production_id),
        "briefs": [
            {
                "id": str(b.id),
                "scene_id": str(b.scene_id),
                "scene_index": b.scene_index,
                "tema": b.tema,
                "funcao_visual": b.funcao_visual.value,
                "assunto_visivel": b.assunto_visivel,
                "contexto_geografico_cultural": b.contexto_geografico_cultural,
                "periodo": b.periodo,
                "tom_editorial": b.tom_editorial,
                "nivel_literalidade": b.nivel_literalidade.value,
                "permitidos": b.permitidos,
                "proibidos": b.proibidos,
                "tipo_ativo_preferido": b.tipo_ativo_preferido.value,
                "template_type_id": b.template_type_id,
            }
            for b in brief_set.briefs
        ],
    }


def _to_production_response(p: Production) -> ProductionResponse:
    return ProductionResponse(
        id=str(p.id),
        title=p.title,
        mode=p.mode.value,
        template_type_id=(
            p.template_selection.template_type.value
            if p.template_selection
            else ""
        ),
        variation_id=(
            p.template_selection.variation_id if p.template_selection else ""
        ),
        current_state=p.current_state.value,
        base_content=p.base_content,
        editorial_context=p.editorial_context,
        restrictions=p.restrictions,
        created_at=p.audit_timestamps.created_at.isoformat(),
        updated_at=p.audit_timestamps.updated_at.isoformat(),
        state_history=[
            StateTransitionResponse(
                from_state=t.from_state.value if t.from_state else None,
                to_state=t.to_state.value,
                occurred_at=t.occurred_at.isoformat(),
                reason=t.reason,
                triggered_by=t.triggered_by,
            )
            for t in p.state_history
        ],
        operator_user_id=p.operator_user_id,
    )


def _to_production_detail_response(
    p: Production,
    composition: CompositionTimeline | None,
    render_job: "object | None",
    narrative: "object | None" = None,
    briefs: "object | None" = None,
) -> ProductionDetailResponse:
    from domain.render.models import RenderJob

    composition_summary = None
    if composition is not None:
        composition_summary = CompositionSummaryResponse(
            id=str(composition.id),
            template_type_id=composition.template_type_id,
            variation_id=composition.variation_id,
            total_duration_seconds=composition.total_duration_seconds,
            slots=[
                CompositionSlotResponse(
                    slot_index=idx,
                    slot_type=s.slot_type,
                    duration_seconds=s.duration_seconds,
                    content_reference=s.content_reference,
                    asset_url=s.asset_url,
                )
                for idx, s in enumerate(composition.slots)
            ],
        )

    render_summary = None
    if render_job is not None and isinstance(render_job, RenderJob):
        render_summary = RenderJobSummaryResponse(
            id=str(render_job.id),
            status=render_job.status.value,
            provider=render_job.provider,
            created_at=render_job.created_at.isoformat(),
            updated_at=render_job.updated_at.isoformat(),
            error_message=render_job.error_message,
        )

    return ProductionDetailResponse(
        id=str(p.id),
        title=p.title,
        mode=p.mode.value,
        template_type_id=(
            p.template_selection.template_type.value
            if p.template_selection
            else ""
        ),
        variation_id=(
            p.template_selection.variation_id if p.template_selection else ""
        ),
        current_state=p.current_state.value,
        base_content=p.base_content,
        editorial_context=p.editorial_context,
        restrictions=p.restrictions,
        created_at=p.audit_timestamps.created_at.isoformat(),
        updated_at=p.audit_timestamps.updated_at.isoformat(),
        operator_user_id=p.operator_user_id,
        organization_id=p.organization_id,
        state_history=[
            StateHistoryEntry(
                from_state=t.from_state.value if t.from_state else None,
                to_state=t.to_state.value,
                occurred_at=t.occurred_at.isoformat(),
                reason=t.reason,
                triggered_by=t.triggered_by,
            )
            for t in p.state_history
        ],
        composition=composition_summary,
        render_job=render_summary,
    )


@router.post("/{production_id}/events", status_code=200)
async def emit_production_event(
    production_id: str,
    request: EmitEventRequest,
    user: CurrentUser,
    session: AsyncSession = Depends(async_session),
) -> dict:
    production = await _load_production(production_id, user.user_id, session)

    event = DomainEvent(
        event_type=request.event_type,
        production_id=production.id,
        payload=request.payload,
        source="manual_emit",
    )
    await _event_bus.emit(event)

    notification = _notification_mapper.map_event(event)

    return {
        "emitted_event": {
            "event_type": event.event_type,
            "production_id": str(event.production_id),
            "timestamp": event.timestamp.isoformat(),
            "source": event.source,
        },
        "notification": (
            {
                "channel": notification.channel,
                "title": notification.title,
                "severity": notification.severity,
            }
            if notification
            else None
        ),
    }


@router.post(
    "/{production_id}/bindings",
    response_model=ManualBindingResponse,
    status_code=201,
)
async def create_binding(
    production_id: str,
    request: ManualBindingCreateRequest,
    user: CurrentUser,
    session: AsyncSession = Depends(async_session),
) -> ManualBindingResponse:
    await _load_production(production_id, user.user_id, session)

    pid = _parse_production_id(production_id)
    scene_id = uuid4()

    binding = await manual_binding_service.bind_asset(
        production_id=pid,
        scene_id=scene_id,
        candidate_id=uuid4(),
        binding_type=BindingType.FIXED,
        asset_url=request.asset_reference,
        asset_title=f"scene-{request.scene_index}",
        bound_by=user.user_id,
        template_type_id="",
    )

    binding.metadata["scene_index"] = request.scene_index
    binding.metadata["asset_type"] = request.asset_type
    binding.metadata["restrictions"] = request.restrictions

    return ManualBindingResponse(
        id=str(binding.id),
        production_id=str(binding.production_id),
        scene_index=request.scene_index,
        asset_reference=binding.asset_url,
        asset_type=request.asset_type,
        bound_by=binding.bound_by,
        created_at=binding.bound_at.isoformat(),
    )


@router.get("/{production_id}/bindings")
async def list_bindings(
    production_id: str,
    user: CurrentUser,
    session: AsyncSession = Depends(async_session),
) -> dict:
    await _load_production(production_id, user.user_id, session)

    pid = _parse_production_id(production_id)
    bindings = await manual_binding_service.get_bindings_for_production(pid)

    return {
        "bindings": [
            {
                "id": str(b.id),
                "production_id": str(b.production_id),
                "scene_index": b.metadata.get("scene_index", 0),
                "asset_reference": b.asset_url,
                "asset_type": b.metadata.get("asset_type", ""),
                "bound_by": b.bound_by,
                "created_at": b.bound_at.isoformat(),
            }
            for b in bindings
        ],
        "count": len(bindings),
    }


@router.delete("/{production_id}/bindings/{binding_id}", status_code=200)
async def delete_binding(
    production_id: str,
    binding_id: str,
    user: CurrentUser,
    session: AsyncSession = Depends(async_session),
) -> dict:
    await _load_production(production_id, user.user_id, session)

    bid = _parse_production_id(binding_id)
    removed = await manual_binding_service.remove_binding(bid, user.user_id)
    if not removed:
        raise AppError(message="Binding not found", status_code=404)

    return {"deleted": str(removed.id)}
