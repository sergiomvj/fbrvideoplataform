from __future__ import annotations

import json
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from domain.structuring.models import NarrativeBase, NarrativeBlock, NarrativeRole
from domain.production.aggregate import Production
from infrastructure.db.models import StructuredNarrativeModel, NarrativeBlockModel


class NarrativeRepository:
    """Repository for structured narratives."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_narrative(self, production: Production, narrative: NarrativeBase) -> UUID:
        existing = await self._get_model(production.id)
        if existing:
            await self._delete_blocks(existing.id)
            await self.session.delete(existing)
            await self.session.flush()

        model = StructuredNarrativeModel(
            id=str(UUID(int=0)),
            production_id=str(production.id),
            template_type_id=narrative.template_type_id,
            variation_id=narrative.variation_id,
            objective=narrative.objective,
            target_duration_seconds=narrative.target_duration_seconds,
        )
        from uuid import uuid4
        model.id = str(uuid4())
        self.session.add(model)
        await self.session.flush()

        for block in narrative.blocks:
            block_model = NarrativeBlockModel(
                id=str(block.id),
                production_id=str(production.id),
                narrative_id=model.id,
                scene_index=block.scene_index,
                role=block.role.value,
                text=block.text,
                estimated_duration_seconds=block.estimated_duration_seconds,
            )
            self.session.add(block_model)

        await self.session.flush()
        return UUID(model.id)

    async def get_narrative(self, production_id: UUID) -> Optional[NarrativeBase]:
        stmt = select(StructuredNarrativeModel).where(
            StructuredNarrativeModel.production_id == str(production_id)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def get_narrative_blocks(self, narrative_id: UUID) -> List[NarrativeBlock]:
        stmt = (
            select(NarrativeBlockModel)
            .where(NarrativeBlockModel.narrative_id == str(narrative_id))
            .order_by(NarrativeBlockModel.scene_index)
        )
        result = await self.session.execute(stmt)
        return [self._block_to_domain(m) for m in result.scalars().all()]

    async def _get_model(self, production_id: UUID) -> Optional[StructuredNarrativeModel]:
        stmt = select(StructuredNarrativeModel).where(
            StructuredNarrativeModel.production_id == str(production_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def _delete_blocks(self, narrative_id: str) -> None:
        stmt = delete(NarrativeBlockModel).where(
            NarrativeBlockModel.narrative_id == narrative_id
        )
        await self.session.execute(stmt)

    def _to_domain(self, model: StructuredNarrativeModel) -> NarrativeBase:
        blocks = []
        if model.blocks:
            blocks = [self._block_to_domain(b) for b in model.blocks]

        return NarrativeBase(
            production_id=UUID(model.production_id),
            template_type_id=model.template_type_id,
            variation_id=model.variation_id,
            objective=model.objective,
            target_duration_seconds=model.target_duration_seconds,
            blocks=blocks,
        )

    def _block_to_domain(self, model: NarrativeBlockModel) -> NarrativeBlock:
        return NarrativeBlock(
            id=UUID(model.id),
            role=NarrativeRole(model.role) if model.role else NarrativeRole.DEVELOPMENT,
            text=model.text or "",
            estimated_duration_seconds=model.estimated_duration_seconds or 0.0,
            scene_index=model.scene_index,
        )
