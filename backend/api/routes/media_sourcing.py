from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from uuid import UUID, uuid4
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from domain.visual_planning import VisualBrief
from domain.media_sourcing import (
    MediaSourceType,
    SourcingResult,
    DiagnosticCategory,
)
from application.services.media_sourcing import media_sourcing_service
from application.services.query_builder.service import query_builder_service
from infrastructure.db.session import async_session
from integrations.stock_media import stock_media_adapter
from integrations.archive_media import archive_media_adapter

router = APIRouter(prefix="/media-sourcing", tags=["media-sourcing"])


class SourceCandidatesRequest(BaseModel):
    production_id: UUID
    scene_id: UUID
    brief_id: Optional[UUID] = None
    tema: str
    funcao_visual: str
    assunto_visivel: str
    contexto_geografico_cultural: str = ""
    periodo: str = ""
    tom_editorial: str = ""
    permitidos: list[str] = []
    proibidos: list[str] = []
    tipo_ativo_preferido: str = "any"
    source_types: Optional[list[str]] = None
    max_results: int = 10


class SourceCandidatesResponse(BaseModel):
    production_id: UUID
    results: list[dict]
    query_attempt_id: Optional[str] = None
    reformulated: bool = False
    eligible_for_review: bool = False


class GetAssetRequest(BaseModel):
    production_id: UUID
    source_type: str
    external_id: str


@router.post("/source", response_model=SourceCandidatesResponse)
async def source_candidates(
    request: SourceCandidatesRequest,
    session: AsyncSession = Depends(async_session),
):
    brief = VisualBrief(
        scene_id=request.scene_id,
        tema=request.tema,
        funcao_visual=request.funcao_visual,
        assunto_visivel=request.assunto_visivel,
        contexto_geografico_cultural=request.contexto_geografico_cultural,
        periodo=request.periodo,
        tom_editorial=request.tom_editorial,
        permitidos=request.permitidos,
        proibidos=request.proibidos,
        tipo_ativo_preferido=request.tipo_ativo_preferido,
    )

    source_types = None
    if request.source_types:
        source_types = [MediaSourceType(st) for st in request.source_types]

    brief_id = request.brief_id or uuid4()

    strategy = query_builder_service.build_strategy_from_brief(brief)

    attempt = await query_builder_service.create_attempt(
        production_id=request.production_id,
        scene_id=request.scene_id,
        brief_id=brief_id,
        strategy=strategy,
        provider_key="multi",
        query_params={
            "tema": request.tema,
            "funcao_visual": request.funcao_visual,
            "source_types": request.source_types,
        },
    )

    results = await media_sourcing_service.source_candidates(
        brief=brief,
        production_id=request.production_id,
        source_types=source_types,
        max_results_per_source=request.max_results,
    )

    total_candidates = sum(len(r.candidates) for r in results)
    has_errors = any(r.error_message for r in results)

    diagnostic = None
    if has_errors:
        diagnostic = DiagnosticCategory.PROVIDER_ERROR
    elif total_candidates == 0:
        diagnostic = DiagnosticCategory.NO_RELEVANT_RESULTS

    await query_builder_service.record_attempt_result(
        attempt_id=attempt.id,
        candidate_count=total_candidates,
        diagnostic=diagnostic,
        diagnostic_details="; ".join(r.error_message for r in results if r.error_message) if has_errors else "",
    )

    reformulated = False
    if query_builder_service.should_requery(attempt):
        reformulation = await query_builder_service.create_reformulation(
            attempt=attempt,
            reason=f"Low results ({total_candidates}), diagnostic: {diagnostic.value if diagnostic else 'none'}",
        )
        reformulated = True

    eligible_for_review = query_builder_service.is_eligible_for_review(attempt)

    return SourceCandidatesResponse(
        production_id=request.production_id,
        results=[
            {
                "source_type": r.provider,
                "outcome": r.outcome.value,
                "candidates": [
                    {
                        "id": c.id.hex,
                        "url": c.url,
                        "thumbnail_url": c.thumbnail_url,
                        "media_type": c.media_type.value,
                        "title": c.title,
                    }
                    for c in r.candidates
                ],
                "error": r.error_message,
                "duration_ms": r.duration_ms,
            }
            for r in results
        ],
        query_attempt_id=attempt.id.hex,
        reformulated=reformulated,
        eligible_for_review=eligible_for_review,
    )


@router.post("/asset")
async def get_asset(request: GetAssetRequest):
    try:
        source_type = MediaSourceType(request.source_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid source_type")

    result = await media_sourcing_service.get_asset_by_source(
        source_type=source_type,
        external_id=request.external_id,
        production_id=request.production_id,
    )

    if not result:
        raise HTTPException(status_code=404, detail="Source adapter not found")

    return {
        "outcome": result.outcome.value,
        "candidates": [
            {
                "id": c.id.hex,
                "url": c.url,
                "thumbnail_url": c.thumbnail_url,
                "media_type": c.media_type.value,
                "title": c.title,
                "description": c.description,
            }
            for c in result.candidates
        ],
        "error": result.error_message,
    }


@router.get("/attempts/{production_id}")
async def list_query_attempts(
    production_id: str,
    session: AsyncSession = Depends(async_session),
) -> dict:
    attempts = await query_builder_service.get_attempts_for_production(UUID(production_id))
    return {
        "production_id": production_id,
        "attempts": [a.to_dict() for a in attempts],
        "total_count": len(attempts),
    }


def register_adapters(service: media_sourcing_service.__class__):
    service.register_adapter(stock_media_adapter)
    service.register_adapter(archive_media_adapter)
