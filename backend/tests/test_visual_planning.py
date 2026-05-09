import pytest

from domain.production.aggregate import Production, TemplateSelection
from domain.production.enums import ProductionMode, TemplateType
from domain.structuring.models import (
    NarrativeBase,
    NarrativeBlock,
    NarrativeRole,
)
from domain.templates.contracts import AssetType
from domain.templates.registry import get_template
from domain.visual_planning.errors import BriefPlanningError
from domain.visual_planning.models import (
    AssetTypePreference,
    LiteralidadeLevel,
    VisualBrief,
    VisualBriefSet,
    VisualFunction,
)
from application.services.structuring.engine import StructuringEngine
from application.services.visual_planning.engine import BriefPlanningEngine

from uuid import uuid4


@pytest.fixture
def engine() -> BriefPlanningEngine:
    return BriefPlanningEngine()


def _make_presenter_production(content: str) -> Production:
    return Production(
        mode=ProductionMode.AUTOMATIC,
        template_selection=TemplateSelection(
            template_type=TemplateType.PRESENTER_SHORT,
            variation_id="1",
        ),
        title="Test Presenter Video",
        base_content=content,
        editorial_context="Testing presenter short visual planning",
        operator_user_id="user-001",
    )


def _make_videodoc_production(content: str) -> Production:
    return Production(
        mode=ProductionMode.AUTOMATIC,
        template_selection=TemplateSelection(
            template_type=TemplateType.VIDEODOC_NARRATED,
            variation_id="1",
        ),
        title="Test VideoDoc",
        base_content=content,
        editorial_context="Testing videodoc narrated visual planning",
        operator_user_id="user-001",
    )


PRESENTER_CONTENT = (
    "Welcome to our channel. "
    "Today we will explore the fascinating world of artificial intelligence. "
    "AI is transforming every industry around the globe. "
    "From healthcare to finance, the applications are endless. "
    "Thank you for watching and see you next time."
)

VIDEODOC_CONTENT = (
    "In this documentary, we examine the rise of renewable energy across the world. "
    "Solar power has become one of the most cost-effective energy sources available today. "
    "Wind farms are popping up in rural areas, providing clean electricity to millions. "
    "Governments are investing heavily in green infrastructure and sustainable policies. "
    "However, challenges remain in energy storage and grid modernization. "
    "Battery technology is improving rapidly, with lithium-ion costs dropping significantly. "
    "Hydrogen fuel cells represent another promising avenue for clean energy storage. "
    "Developing nations are leapfrogging fossil fuels entirely in some regions. "
    "The transition to renewables is not just environmental, it is economic. "
    "Companies that embrace sustainability are seeing stronger financial performance. "
    "The future of energy is bright, but it requires continued innovation. "
    "Thank you for joining us on this exploration of renewable energy."
)


async def _structure_presenter() -> tuple[NarrativeBase, "TemplateContract"]:
    structuring_engine = StructuringEngine()
    production = _make_presenter_production(PRESENTER_CONTENT)
    narrative = await structuring_engine.structure(production)
    template = get_template("presenter_short")
    assert template is not None
    return narrative, template


async def _structure_videodoc() -> tuple[NarrativeBase, "TemplateContract"]:
    structuring_engine = StructuringEngine()
    production = _make_videodoc_production(VIDEODOC_CONTENT)
    narrative = await structuring_engine.structure(production)
    template = get_template("videodoc_narrated")
    assert template is not None
    return narrative, template


class TestPresenterShortBriefs:
    @pytest.mark.asyncio
    async def test_generates_valid_brief_set(self, engine: BriefPlanningEngine) -> None:
        narrative, template = await _structure_presenter()
        result = await engine.generate_briefs(narrative, template)

        assert isinstance(result, VisualBriefSet)
        assert result.production_id == narrative.production_id
        assert len(result.briefs) > 0

    @pytest.mark.asyncio
    async def test_briefs_have_all_required_fields(self, engine: BriefPlanningEngine) -> None:
        narrative, template = await _structure_presenter()
        result = await engine.generate_briefs(narrative, template)

        for brief in result.briefs:
            assert isinstance(brief, VisualBrief)
            assert brief.tema != ""
            assert brief.assunto_visivel != ""
            assert isinstance(brief.funcao_visual, VisualFunction)
            assert isinstance(brief.nivel_literalidade, LiteralidadeLevel)
            assert isinstance(brief.tipo_ativo_preferido, AssetTypePreference)
            assert brief.template_type_id == "presenter_short"
            assert brief.scene_index >= 0
            assert brief.id is not None
            assert brief.scene_id is not None

    @pytest.mark.asyncio
    async def test_literalidade_alta_for_presenter(self, engine: BriefPlanningEngine) -> None:
        narrative, template = await _structure_presenter()
        result = await engine.generate_briefs(narrative, template)

        for brief in result.briefs:
            assert brief.nivel_literalidade == LiteralidadeLevel.ALTA

    @pytest.mark.asyncio
    async def test_asset_preference_image_for_presenter(self, engine: BriefPlanningEngine) -> None:
        narrative, template = await _structure_presenter()
        result = await engine.generate_briefs(narrative, template)

        for brief in result.briefs:
            assert brief.tipo_ativo_preferido == AssetTypePreference.IMAGE


class TestVideodocNarratedBriefs:
    @pytest.mark.asyncio
    async def test_generates_valid_brief_set(self, engine: BriefPlanningEngine) -> None:
        narrative, template = await _structure_videodoc()
        result = await engine.generate_briefs(narrative, template)

        assert isinstance(result, VisualBriefSet)
        assert result.production_id == narrative.production_id
        assert len(result.briefs) > 0

    @pytest.mark.asyncio
    async def test_briefs_have_all_required_fields(self, engine: BriefPlanningEngine) -> None:
        narrative, template = await _structure_videodoc()
        result = await engine.generate_briefs(narrative, template)

        for brief in result.briefs:
            assert isinstance(brief, VisualBrief)
            assert brief.tema != ""
            assert brief.assunto_visivel != ""
            assert isinstance(brief.funcao_visual, VisualFunction)
            assert isinstance(brief.nivel_literalidade, LiteralidadeLevel)
            assert isinstance(brief.tipo_ativo_preferido, AssetTypePreference)
            assert brief.template_type_id == "videodoc_narrated"
            assert brief.scene_index >= 0
            assert brief.id is not None
            assert brief.scene_id is not None

    @pytest.mark.asyncio
    async def test_literalidade_media_for_videodoc(self, engine: BriefPlanningEngine) -> None:
        narrative, template = await _structure_videodoc()
        result = await engine.generate_briefs(narrative, template)

        for brief in result.briefs:
            assert brief.nivel_literalidade == LiteralidadeLevel.MEDIA

    @pytest.mark.asyncio
    async def test_asset_preference_any_for_videodoc(self, engine: BriefPlanningEngine) -> None:
        narrative, template = await _structure_videodoc()
        result = await engine.generate_briefs(narrative, template)

        for brief in result.briefs:
            assert brief.tipo_ativo_preferido == AssetTypePreference.ANY


class TestSceneBriefTraceability:
    @pytest.mark.asyncio
    async def test_presenter_brief_count_matches_blocks(self, engine: BriefPlanningEngine) -> None:
        narrative, template = await _structure_presenter()
        result = await engine.generate_briefs(narrative, template)

        assert len(result.briefs) == len(narrative.blocks)

    @pytest.mark.asyncio
    async def test_videodoc_brief_count_matches_blocks(self, engine: BriefPlanningEngine) -> None:
        narrative, template = await _structure_videodoc()
        result = await engine.generate_briefs(narrative, template)

        assert len(result.briefs) == len(narrative.blocks)

    @pytest.mark.asyncio
    async def test_presenter_scene_indices_match(self, engine: BriefPlanningEngine) -> None:
        narrative, template = await _structure_presenter()
        result = await engine.generate_briefs(narrative, template)

        for block, brief in zip(narrative.blocks, result.briefs):
            assert brief.scene_index == block.scene_index
            assert brief.scene_id == block.id

    @pytest.mark.asyncio
    async def test_videodoc_scene_indices_match(self, engine: BriefPlanningEngine) -> None:
        narrative, template = await _structure_videodoc()
        result = await engine.generate_briefs(narrative, template)

        for block, brief in zip(narrative.blocks, result.briefs):
            assert brief.scene_index == block.scene_index
            assert brief.scene_id == block.id


class TestVisualFunctionMapping:
    @pytest.mark.asyncio
    async def test_opening_maps_to_contexto_ambiental(self, engine: BriefPlanningEngine) -> None:
        narrative, template = await _structure_presenter()
        result = await engine.generate_briefs(narrative, template)

        opening_blocks = [
            b for b, bl in zip(narrative.blocks, result.briefs)
            if b.role == NarrativeRole.OPENING
        ]
        if opening_blocks:
            for block, brief in zip(narrative.blocks, result.briefs):
                if block.role == NarrativeRole.OPENING:
                    assert brief.funcao_visual == VisualFunction.CONTEXTO_AMBIENTAL

    @pytest.mark.asyncio
    async def test_closing_maps_to_contexto_ambiental(self, engine: BriefPlanningEngine) -> None:
        narrative, template = await _structure_presenter()
        result = await engine.generate_briefs(narrative, template)

        for block, brief in zip(narrative.blocks, result.briefs):
            if block.role == NarrativeRole.CLOSING:
                assert brief.funcao_visual == VisualFunction.CONTEXTO_AMBIENTAL

    @pytest.mark.asyncio
    async def test_development_maps_to_cobertura_broll(self, engine: BriefPlanningEngine) -> None:
        narrative, template = await _structure_videodoc()
        result = await engine.generate_briefs(narrative, template)

        for block, brief in zip(narrative.blocks, result.briefs):
            if block.role == NarrativeRole.DEVELOPMENT:
                assert brief.funcao_visual == VisualFunction.COBERTURA_BROLL


class TestBriefPlanningFailures:
    @pytest.mark.asyncio
    async def test_empty_narrative_raises_error(self, engine: BriefPlanningEngine) -> None:
        narrative = NarrativeBase(
            production_id=uuid4(),
            template_type_id="presenter_short",
            variation_id="1",
            objective="Test",
            target_duration_seconds=60.0,
            blocks=[],
        )
        template = get_template("presenter_short")
        assert template is not None

        with pytest.raises(BriefPlanningError) as exc_info:
            await engine.generate_briefs(narrative, template)
        assert exc_info.value.reason == "empty_narrative"

    @pytest.mark.asyncio
    async def test_permitidos_and_proibidos_populated(self, engine: BriefPlanningEngine) -> None:
        narrative, template = await _structure_presenter()
        result = await engine.generate_briefs(narrative, template)

        for brief in result.briefs:
            assert len(brief.permitidos) > 0
            assert len(brief.proibidos) > 0
