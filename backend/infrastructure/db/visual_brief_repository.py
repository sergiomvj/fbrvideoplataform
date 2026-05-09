from __future__ import annotations

import json
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from domain.visual_planning.models import (
    VisualBrief,
    VisualBriefSet,
    VisualFunction,
    LiteralidadeLevel,
    AssetTypePreference,
)
from domain.production.aggregate import Production
from infrastructure.db.models import VisualBriefModel


class VisualBriefRepository:
    """Repository for visual briefs."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_briefs(self, production: Production, briefs: List[VisualBrief]) -> List[UUID]:
        await self._delete_by_production(production.id)

        ids: list[UUID] = []
        for brief in briefs:
            model = VisualBriefModel(
                id=str(brief.id),
                production_id=str(production.id),
                scene_id=str(brief.scene_id),
                scene_index=brief.scene_index,
                tema=brief.tema,
                funcao_visual=brief.funcao_visual.value,
                assunto_visivel=brief.assunto_visivel,
                contexto_geografico_cultural=brief.contexto_geografico_cultural,
                periodo=brief.periodo,
                tom_editorial=brief.tom_editorial,
                nivel_literalidade=brief.nivel_literalidade.value,
                permitidos=json.dumps(brief.permitidos),
                proibidos=json.dumps(brief.proibidos),
                tipo_ativo_preferido=brief.tipo_ativo_preferido.value,
                template_type_id=brief.template_type_id,
            )
            self.session.add(model)
            ids.append(brief.id)

        await self.session.flush()
        return ids

    async def get_briefs_by_production(self, production_id: UUID) -> List[VisualBrief]:
        stmt = (
            select(VisualBriefModel)
            .where(VisualBriefModel.production_id == str(production_id))
            .order_by(VisualBriefModel.scene_index)
        )
        result = await self.session.execute(stmt)
        return [self._to_domain(m) for m in result.scalars().all()]

    async def get_brief_by_scene(self, production_id: UUID, scene_id: UUID) -> Optional[VisualBrief]:
        stmt = select(VisualBriefModel).where(
            VisualBriefModel.production_id == str(production_id),
            VisualBriefModel.scene_id == str(scene_id),
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def _delete_by_production(self, production_id: UUID) -> None:
        stmt = delete(VisualBriefModel).where(
            VisualBriefModel.production_id == str(production_id)
        )
        await self.session.execute(stmt)

    def _to_domain(self, model: VisualBriefModel) -> VisualBrief:
        return VisualBrief(
            id=UUID(model.id),
            scene_id=UUID(model.scene_id),
            scene_index=model.scene_index,
            tema=model.tema,
            funcao_visual=VisualFunction(model.funcao_visual),
            assunto_visivel=model.assunto_visivel,
            contexto_geografico_cultural=model.contexto_geografico_cultural or "",
            periodo=model.periodo or "",
            tom_editorial=model.tom_editorial or "",
            nivel_literalidade=LiteralidadeLevel(model.nivel_literalidade),
            permitidos=json.loads(model.permitidos) if model.permitidos else [],
            proibidos=json.loads(model.proibidos) if model.proibidos else [],
            tipo_ativo_preferido=AssetTypePreference(model.tipo_ativo_preferido),
            template_type_id=model.template_type_id or "",
        )
