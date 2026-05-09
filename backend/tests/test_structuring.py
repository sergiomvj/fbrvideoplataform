import pytest

from domain.production.aggregate import Production, TemplateSelection
from domain.production.enums import ProductionMode, TemplateType, WorkflowState
from domain.structuring.errors import StructuringError, StructuringReason
from domain.structuring.models import NarrativeBase, NarrativeBlock, NarrativeRole
from domain.templates.registry import get_template
from application.services.structuring.engine import StructuringEngine


@pytest.fixture
def engine() -> StructuringEngine:
    return StructuringEngine()


def _make_presenter_production(content: str) -> Production:
    return Production(
        mode=ProductionMode.AUTOMATIC,
        template_selection=TemplateSelection(
            template_type=TemplateType.PRESENTER_SHORT,
            variation_id="1",
        ),
        title="Test Presenter Video",
        base_content=content,
        editorial_context="Testing presenter short structuring",
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
        editorial_context="Testing videodoc narrated structuring",
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


class TestPresenterShortStructuring:
    @pytest.mark.asyncio
    async def test_produces_valid_narrative_base(self, engine: StructuringEngine) -> None:
        production = _make_presenter_production(PRESENTER_CONTENT)
        result = await engine.structure(production)

        assert isinstance(result, NarrativeBase)
        assert result.production_id == production.id
        assert result.template_type_id == "presenter_short"
        assert result.variation_id == "1"
        assert result.objective != ""
        assert result.target_duration_seconds == 60.0

    @pytest.mark.asyncio
    async def test_blocks_within_scene_limits(self, engine: StructuringEngine) -> None:
        production = _make_presenter_production(PRESENTER_CONTENT)
        result = await engine.structure(production)

        template = get_template("presenter_short")
        assert template is not None
        assert len(result.blocks) >= template.composition_constraints.min_scenes
        assert len(result.blocks) <= template.composition_constraints.max_scenes

    @pytest.mark.asyncio
    async def test_duration_within_limits(self, engine: StructuringEngine) -> None:
        production = _make_presenter_production(PRESENTER_CONTENT)
        result = await engine.structure(production)

        assert result.total_duration <= 60.0

    @pytest.mark.asyncio
    async def test_blocks_have_valid_roles(self, engine: StructuringEngine) -> None:
        production = _make_presenter_production(PRESENTER_CONTENT)
        result = await engine.structure(production)

        assert result.blocks[0].role == NarrativeRole.OPENING
        assert result.blocks[-1].role == NarrativeRole.CLOSING
        for block in result.blocks[1:-1]:
            assert block.role == NarrativeRole.DEVELOPMENT

    @pytest.mark.asyncio
    async def test_blocks_have_sequential_scene_index(self, engine: StructuringEngine) -> None:
        production = _make_presenter_production(PRESENTER_CONTENT)
        result = await engine.structure(production)

        for i, block in enumerate(result.blocks):
            assert block.scene_index == i


class TestVideodocNarratedStructuring:
    @pytest.mark.asyncio
    async def test_produces_valid_narrative_base(self, engine: StructuringEngine) -> None:
        production = _make_videodoc_production(VIDEODOC_CONTENT)
        result = await engine.structure(production)

        assert isinstance(result, NarrativeBase)
        assert result.production_id == production.id
        assert result.template_type_id == "videodoc_narrated"
        assert result.variation_id == "1"
        assert result.target_duration_seconds == 180.0

    @pytest.mark.asyncio
    async def test_blocks_within_scene_limits(self, engine: StructuringEngine) -> None:
        production = _make_videodoc_production(VIDEODOC_CONTENT)
        result = await engine.structure(production)

        template = get_template("videodoc_narrated")
        assert template is not None
        assert len(result.blocks) >= template.composition_constraints.min_scenes
        assert len(result.blocks) <= template.composition_constraints.max_scenes

    @pytest.mark.asyncio
    async def test_duration_within_limits(self, engine: StructuringEngine) -> None:
        production = _make_videodoc_production(VIDEODOC_CONTENT)
        result = await engine.structure(production)

        assert result.total_duration <= 180.0

    @pytest.mark.asyncio
    async def test_richer_role_distribution(self, engine: StructuringEngine) -> None:
        production = _make_videodoc_production(VIDEODOC_CONTENT)
        result = await engine.structure(production)

        roles = {b.role for b in result.blocks}
        assert NarrativeRole.OPENING in roles
        assert NarrativeRole.CLOSING in roles

    @pytest.mark.asyncio
    async def test_minimum_blocks_for_videodoc(self, engine: StructuringEngine) -> None:
        production = _make_videodoc_production(VIDEODOC_CONTENT)
        result = await engine.structure(production)

        assert len(result.blocks) >= 2


class TestStructuringFailures:
    @pytest.mark.asyncio
    async def test_empty_content_raises_insufficient(self, engine: StructuringEngine) -> None:
        production = _make_presenter_production("")
        with pytest.raises(StructuringError) as exc_info:
            await engine.structure(production)
        assert exc_info.value.reason == StructuringReason.INSUFFICIENT_CONTENT

    @pytest.mark.asyncio
    async def test_very_short_content_raises_insufficient(self, engine: StructuringEngine) -> None:
        production = _make_presenter_production("Hi.")
        with pytest.raises(StructuringError) as exc_info:
            await engine.structure(production)
        assert exc_info.value.reason == StructuringReason.INSUFFICIENT_CONTENT

    @pytest.mark.asyncio
    async def test_no_template_selection_raises_incompatible(self, engine: StructuringEngine) -> None:
        production = Production(
            mode=ProductionMode.AUTOMATIC,
            base_content="Some content here that is long enough.",
            operator_user_id="user-001",
        )
        with pytest.raises(StructuringError) as exc_info:
            await engine.structure(production)
        assert exc_info.value.reason == StructuringReason.TEMPLATE_INCOMPATIBLE


class TestTemplateConstraints:
    @pytest.mark.asyncio
    async def test_presenter_blocks_respect_constraints(self, engine: StructuringEngine) -> None:
        production = _make_presenter_production(PRESENTER_CONTENT)
        result = await engine.structure(production)

        template = get_template("presenter_short")
        assert template is not None
        constraints = template.composition_constraints
        duration_limit = template.duration_constraint.max_seconds

        assert constraints.min_scenes <= len(result.blocks) <= constraints.max_scenes
        assert result.total_duration <= duration_limit

    @pytest.mark.asyncio
    async def test_videodoc_blocks_respect_constraints(self, engine: StructuringEngine) -> None:
        production = _make_videodoc_production(VIDEODOC_CONTENT)
        result = await engine.structure(production)

        template = get_template("videodoc_narrated")
        assert template is not None
        constraints = template.composition_constraints
        duration_limit = template.duration_constraint.max_seconds

        assert constraints.min_scenes <= len(result.blocks) <= constraints.max_scenes
        assert result.total_duration <= duration_limit

    @pytest.mark.asyncio
    async def test_long_content_duration_capped(self, engine: StructuringEngine) -> None:
        long_content = " ".join(
            f"Sentence number {i} with enough words to be a valid segment."
            for i in range(100)
        )
        production = _make_videodoc_production(long_content)
        result = await engine.structure(production)

        assert result.total_duration <= 180.0


class TestNarrativeBaseProperties:
    @pytest.mark.asyncio
    async def test_total_duration_property(self, engine: StructuringEngine) -> None:
        production = _make_presenter_production(PRESENTER_CONTENT)
        result = await engine.structure(production)

        expected = sum(b.estimated_duration_seconds for b in result.blocks)
        assert result.total_duration == pytest.approx(expected)

    @pytest.mark.asyncio
    async def test_objective_derived_from_production(self, engine: StructuringEngine) -> None:
        production = _make_presenter_production(PRESENTER_CONTENT)
        result = await engine.structure(production)

        assert "Test Presenter Video" in result.objective
        assert "Testing presenter short structuring" in result.objective
