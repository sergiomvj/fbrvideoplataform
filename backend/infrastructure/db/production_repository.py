from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.production import (
    Production,
    TemplateSelection,
    AuditTimestamps,
    StateTransition,
    ProductionMode,
    TemplateType,
    WorkflowState,
)
from infrastructure.db.models import (
    ProductionModel,
    ProductionRestrictionModel,
    ProductionStateTransitionModel,
)


class ProductionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, production: Production) -> Production:
        stmt = select(ProductionModel).where(ProductionModel.id == str(production.id))
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            await self.session.delete(existing)
            await self.session.flush()
        model = self._to_model(production)
        self.session.add(model)
        await self.session.flush()
        return production

    async def get_by_id(self, production_id: UUID) -> Production | None:
        stmt = select(ProductionModel).where(
            ProductionModel.id == str(production_id)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def list_by_operator(
        self, operator_user_id: str
    ) -> list[Production]:
        stmt = select(ProductionModel).where(
            ProductionModel.operator_user_id == operator_user_id
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    def _to_domain(self, model: ProductionModel) -> Production:
        production = Production.__new__(Production)
        production.id = UUID(model.id)
        production.mode = ProductionMode(model.mode)
        production.template_selection = (
            TemplateSelection(
                template_type=TemplateType(model.template_type_id),
                variation_id=model.variation_id or "",
            )
            if model.template_type_id
            else None
        )
        production.current_state = WorkflowState(model.current_state)
        production.title = model.title
        production.base_content = model.base_content or ""
        production.editorial_context = model.editorial_context or ""
        production.restrictions = [r.restriction for r in model.restrictions]
        production.audit_timestamps = AuditTimestamps(
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
        production.state_history = sorted(
            [
                StateTransition(
                    from_state=(
                        WorkflowState(t.from_state) if t.from_state else None
                    ),
                    to_state=WorkflowState(t.to_state),
                    occurred_at=t.occurred_at,
                    reason=t.reason or "",
                    triggered_by=t.triggered_by or "",
                )
                for t in model.state_transitions
            ],
            key=lambda x: x.occurred_at,
        )
        production.operator_user_id = str(model.operator_user_id)
        production.organization_id = str(model.organization_id)
        return production

    def _to_model(self, production: Production) -> ProductionModel:
        model = ProductionModel(
            id=str(production.id),
            organization_id=production.organization_id,
            operator_user_id=production.operator_user_id,
            mode=production.mode.value,
            template_type_id=(
                production.template_selection.template_type.value
                if production.template_selection
                else ""
            ),
            variation_id=(
                production.template_selection.variation_id
                if production.template_selection
                else None
            ),
            title=production.title,
            base_content=production.base_content,
            editorial_context=production.editorial_context,
            current_state=production.current_state.value,
            created_at=production.audit_timestamps.created_at,
            updated_at=production.audit_timestamps.updated_at,
        )
        model.restrictions = [
            ProductionRestrictionModel(
                production_id=str(production.id),
                restriction=r,
            )
            for r in production.restrictions
        ]
        model.state_transitions = [
            ProductionStateTransitionModel(
                production_id=str(production.id),
                from_state=t.from_state.value if t.from_state else None,
                to_state=t.to_state.value,
                reason=t.reason,
                triggered_by=t.triggered_by,
                occurred_at=t.occurred_at,
            )
            for t in production.state_history
        ]
        return model
