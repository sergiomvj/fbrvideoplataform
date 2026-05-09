from __future__ import annotations

from uuid import uuid4

from domain.structuring.models import NarrativeBase, NarrativeBlock, NarrativeRole
from domain.templates.contracts import AssetType, TemplateContract
from domain.visual_planning.errors import BriefPlanningError
from domain.visual_planning.models import (
    AssetTypePreference,
    LiteralidadeLevel,
    VisualBrief,
    VisualBriefSet,
    VisualFunction,
)

ROLE_TO_FUNCTION: dict[NarrativeRole, VisualFunction] = {
    NarrativeRole.OPENING: VisualFunction.CONTEXTO_AMBIENTAL,
    NarrativeRole.DEVELOPMENT: VisualFunction.COBERTURA_BROLL,
    NarrativeRole.CLIMAX: VisualFunction.EVIDENCIA_LITERAL,
    NarrativeRole.CLOSING: VisualFunction.CONTEXTO_AMBIENTAL,
    NarrativeRole.TRANSITION: VisualFunction.METAFORA_CONTROLADA,
    NarrativeRole.CONTEXT: VisualFunction.PROVA_DOCUMENTAL,
}

DEFAULT_PROIBIDOS = [
    "violencia explicita",
    "conteudo sexual",
    "imagens chocantes",
    "criancas em situacoes de risco",
]


class BriefPlanningEngine:
    async def generate_briefs(
        self,
        narrative_base: NarrativeBase,
        template: TemplateContract,
    ) -> VisualBriefSet:
        if not narrative_base.blocks:
            raise BriefPlanningError(
                message="Cannot generate briefs from empty narrative",
                reason="empty_narrative",
            )

        literalidade = self._derive_literalidade(template)
        asset_preference = self._derive_asset_preference(template)
        tom_editorial = self._derive_tom_editorial(template)

        briefs: list[VisualBrief] = []
        for block in narrative_base.blocks:
            brief = self._generate_brief(
                block=block,
                literalidade=literalidade,
                asset_preference=asset_preference,
                tom_editorial=tom_editorial,
                template_type_id=template.type_id,
            )
            briefs.append(brief)

        if len(briefs) != len(narrative_base.blocks):
            raise BriefPlanningError(
                message="Brief count does not match block count",
                reason="traceability_mismatch",
            )

        return VisualBriefSet(
            production_id=narrative_base.production_id,
            briefs=briefs,
        )

    def _generate_brief(
        self,
        block: NarrativeBlock,
        literalidade: LiteralidadeLevel,
        asset_preference: AssetTypePreference,
        tom_editorial: str,
        template_type_id: str,
    ) -> VisualBrief:
        tema = self._derive_tema(block)
        funcao_visual = ROLE_TO_FUNCTION.get(
            block.role, VisualFunction.COBERTURA_BROLL
        )
        assunto_visivel = self._derive_assunto_visivel(block)

        return VisualBrief(
            id=uuid4(),
            scene_id=block.id,
            scene_index=block.scene_index,
            tema=tema,
            funcao_visual=funcao_visual,
            assunto_visivel=assunto_visivel,
            contexto_geografico_cultural="",
            periodo="",
            tom_editorial=tom_editorial,
            nivel_literalidade=literalidade,
            permitidos=[tema],
            proibidos=list(DEFAULT_PROIBIDOS),
            tipo_ativo_preferido=asset_preference,
            template_type_id=template_type_id,
        )

    def _derive_tema(self, block: NarrativeBlock) -> str:
        words = block.text.split()
        if len(words) <= 6:
            return block.text
        return " ".join(words[:6])

    def _derive_assunto_visivel(self, block: NarrativeBlock) -> str:
        return block.text[:120] if len(block.text) > 120 else block.text

    def _derive_literalidade(self, template: TemplateContract) -> LiteralidadeLevel:
        if template.type_id == "presenter_short":
            return LiteralidadeLevel.ALTA
        return LiteralidadeLevel.MEDIA

    def _derive_asset_preference(
        self, template: TemplateContract
    ) -> AssetTypePreference:
        types = template.supported_asset_types
        if AssetType.IMAGE in types and AssetType.VIDEO in types:
            return AssetTypePreference.ANY
        if AssetType.VIDEO in types:
            return AssetTypePreference.VIDEO
        return AssetTypePreference.IMAGE

    def _derive_tom_editorial(self, template: TemplateContract) -> str:
        if template.type_id == "presenter_short":
            return "institucional"
        return "documentario"
