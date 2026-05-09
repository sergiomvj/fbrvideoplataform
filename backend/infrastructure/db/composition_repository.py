from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.composition.models import CompositionTimeline, TimelineSlot
from infrastructure.db.models import CompositionModel, CompositionSlotModel


class CompositionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, composition: CompositionTimeline) -> CompositionTimeline:
        existing = await self._get_model(composition.id)
        if existing:
            await self.session.delete(existing)
            await self.session.flush()
        model = self._to_model(composition)
        self.session.add(model)
        await self.session.flush()
        return composition

    async def get_by_production(
        self, production_id: UUID
    ) -> CompositionTimeline | None:
        stmt = select(CompositionModel).where(
            CompositionModel.production_id == str(production_id)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def _get_model(self, composition_id: UUID) -> CompositionModel | None:
        stmt = select(CompositionModel).where(
            CompositionModel.id == str(composition_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    def _to_domain(self, model: CompositionModel) -> CompositionTimeline:
        slots = [
            TimelineSlot(
                slot_type=s.slot_type,
                duration_seconds=s.duration_seconds,
                content_reference=s.content_reference or "",
                asset_url=s.asset_url,
            )
            for s in model.slots
        ]
        return CompositionTimeline(
            id=UUID(model.id),
            production_id=UUID(model.production_id),
            template_type_id=model.template_type_id or "",
            variation_id=model.variation_id or "1",
            slots=slots,
            total_duration_seconds=model.total_duration_seconds or 0.0,
        )

    def _to_model(self, composition: CompositionTimeline) -> CompositionModel:
        model = CompositionModel(
            id=str(composition.id),
            production_id=str(composition.production_id),
            template_type_id=composition.template_type_id or None,
            variation_id=composition.variation_id or None,
            total_duration_seconds=composition.total_duration_seconds,
        )
        model.slots = [
            CompositionSlotModel(
                composition_id=str(composition.id),
                slot_index=idx,
                slot_type=s.slot_type,
                duration_seconds=s.duration_seconds,
                content_reference=s.content_reference,
                asset_url=s.asset_url,
            )
            for idx, s in enumerate(composition.slots)
        ]
        return model
