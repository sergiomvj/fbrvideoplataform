import pytest
from uuid import uuid4

from domain.composition.models import CompositionTimeline, TimelineSlot
from domain.composition.presenter_short.composer import (
    PresenterShortComposer,
    MAX_DURATION as PRESENTER_MAX_DURATION,
    MAX_SCENES as PRESENTER_MAX_SCENES,
)
from domain.composition.videodoc.composer import (
    VideoDocComposer,
    MAX_DURATION as VIDEODOC_MAX_DURATION,
    MIN_SCENES as VIDEODOC_MIN_SCENES,
    MAX_SCENES as VIDEODOC_MAX_SCENES,
)
from domain.human_review.bindings import ManualBinding
from domain.structuring.models import NarrativeBase, NarrativeBlock, NarrativeRole


def _make_narrative_base(
    template_type_id: str = "presenter_short",
    variation_id: str = "1",
    num_blocks: int = 3,
    duration_per_block: float = 10.0,
) -> NarrativeBase:
    production_id = uuid4()
    blocks = [
        NarrativeBlock(
            role=NarrativeRole.OPENING if i == 0 else (
                NarrativeRole.CLOSING if i == num_blocks - 1 else NarrativeRole.DEVELOPMENT
            ),
            text=f"Block {i} content text",
            estimated_duration_seconds=duration_per_block,
            scene_index=i,
        )
        for i in range(num_blocks)
    ]
    return NarrativeBase(
        production_id=production_id,
        template_type_id=template_type_id,
        variation_id=variation_id,
        objective="Test objective",
        target_duration_seconds=duration_per_block * num_blocks,
        blocks=blocks,
    )


class TestPresenterShortComposition:
    @pytest.mark.asyncio
    async def test_max_duration_enforced(self) -> None:
        narrative = _make_narrative_base(num_blocks=5, duration_per_block=20.0)
        composer = PresenterShortComposer()
        result = await composer.compose(narrative, {}, [], "1")
        assert result.total_duration_seconds <= PRESENTER_MAX_DURATION

    @pytest.mark.asyncio
    async def test_max_scenes_enforced(self) -> None:
        narrative = _make_narrative_base(num_blocks=10)
        composer = PresenterShortComposer()
        result = await composer.compose(narrative, {}, [], "1")
        timed_slots = [s for s in result.slots if s.slot_type == "presenter"]
        assert len(timed_slots) <= PRESENTER_MAX_SCENES

    @pytest.mark.asyncio
    async def test_template_type_set(self) -> None:
        narrative = _make_narrative_base()
        composer = PresenterShortComposer()
        result = await composer.compose(narrative, {}, [], "1")
        assert result.template_type_id == "presenter_short"

    @pytest.mark.asyncio
    async def test_variation_id_preserved(self) -> None:
        narrative = _make_narrative_base(variation_id="3")
        composer = PresenterShortComposer()
        result = await composer.compose(narrative, {}, [], "3")
        assert result.variation_id == "3"

    @pytest.mark.asyncio
    async def test_has_presenter_slots(self) -> None:
        narrative = _make_narrative_base()
        composer = PresenterShortComposer()
        result = await composer.compose(narrative, {}, [], "1")
        presenter_slots = [s for s in result.slots if s.slot_type == "presenter"]
        assert len(presenter_slots) >= 1

    @pytest.mark.asyncio
    async def test_has_background_slots(self) -> None:
        narrative = _make_narrative_base()
        composer = PresenterShortComposer()
        result = await composer.compose(narrative, {}, [], "1")
        bg_slots = [s for s in result.slots if s.slot_type == "background"]
        assert len(bg_slots) >= 1

    @pytest.mark.asyncio
    async def test_has_narration_slot(self) -> None:
        narrative = _make_narrative_base()
        composer = PresenterShortComposer()
        result = await composer.compose(narrative, {}, [], "1")
        narration_slots = [s for s in result.slots if s.slot_type == "narration"]
        assert len(narration_slots) == 1


class TestVideoDocComposition:
    @pytest.mark.asyncio
    async def test_max_duration_enforced(self) -> None:
        narrative = _make_narrative_base(
            template_type_id="videodoc_narrated",
            num_blocks=12,
            duration_per_block=20.0,
        )
        composer = VideoDocComposer()
        result = await composer.compose(narrative, {}, [], "1")
        assert result.total_duration_seconds <= VIDEODOC_MAX_DURATION

    @pytest.mark.asyncio
    async def test_max_scenes_enforced(self) -> None:
        narrative = _make_narrative_base(
            template_type_id="videodoc_narrated",
            num_blocks=20,
        )
        composer = VideoDocComposer()
        result = await composer.compose(narrative, {}, [], "1")
        timed_slots = [s for s in result.slots if s.duration_seconds > 0]
        assert len(timed_slots) <= VIDEODOC_MAX_SCENES

    @pytest.mark.asyncio
    async def test_min_scenes_enforced(self) -> None:
        narrative = _make_narrative_base(
            template_type_id="videodoc_narrated",
            num_blocks=1,
        )
        composer = VideoDocComposer()
        result = await composer.compose(narrative, {}, [], "1")
        timed_slots = [s for s in result.slots if s.duration_seconds > 0]
        assert len(timed_slots) >= VIDEODOC_MIN_SCENES

    @pytest.mark.asyncio
    async def test_template_type_set(self) -> None:
        narrative = _make_narrative_base(template_type_id="videodoc_narrated")
        composer = VideoDocComposer()
        result = await composer.compose(narrative, {}, [], "1")
        assert result.template_type_id == "videodoc_narrated"

    @pytest.mark.asyncio
    async def test_has_narration_slot(self) -> None:
        narrative = _make_narrative_base(template_type_id="videodoc_narrated")
        composer = VideoDocComposer()
        result = await composer.compose(narrative, {}, [], "1")
        narration = [s for s in result.slots if s.slot_type == "narration"]
        assert len(narration) == 1

    @pytest.mark.asyncio
    async def test_variation_1_has_broll(self) -> None:
        narrative = _make_narrative_base(
            template_type_id="videodoc_narrated",
            num_blocks=3,
        )
        composer = VideoDocComposer()
        result = await composer.compose(narrative, {}, [], "1")
        broll = [s for s in result.slots if s.content_reference.startswith("broll_")]
        assert len(broll) >= 1

    @pytest.mark.asyncio
    async def test_variation_2_presenter_focused(self) -> None:
        narrative = _make_narrative_base(
            template_type_id="videodoc_narrated",
            num_blocks=3,
        )
        composer = VideoDocComposer()
        result = await composer.compose(narrative, {}, [], "2")
        presenter_slots = [s for s in result.slots if s.slot_type == "presenter"]
        assert len(presenter_slots) >= 1


class TestManualBindingOverride:
    @pytest.mark.asyncio
    async def test_manual_binding_overrides_presenter(self) -> None:
        narrative = _make_narrative_base(num_blocks=3)
        scene_id = narrative.blocks[0].id
        manual_url = "https://custom.asset/my_presenter.jpg"
        bindings = [
            ManualBinding(
                production_id=narrative.production_id,
                scene_id=scene_id,
                asset_reference=manual_url,
                asset_type="image",
                bound_by="operator",
            )
        ]
        approved = {narrative.blocks[1].id: "https://approved.asset/img.jpg"}

        composer = PresenterShortComposer()
        result = await composer.compose(narrative, approved, bindings, "1")

        bound_slot = next(
            s for s in result.slots
            if s.slot_type == "presenter" and s.content_reference == "Block 0 content text"
        )
        assert bound_slot.asset_url == manual_url

    @pytest.mark.asyncio
    async def test_manual_binding_overrides_videodoc(self) -> None:
        narrative = _make_narrative_base(
            template_type_id="videodoc_narrated",
            num_blocks=3,
        )
        scene_id = narrative.blocks[1].id
        manual_url = "https://custom.asset/videodoc_override.mp4"
        bindings = [
            ManualBinding(
                production_id=narrative.production_id,
                scene_id=scene_id,
                asset_reference=manual_url,
                asset_type="video",
                bound_by="operator",
            )
        ]

        composer = VideoDocComposer()
        result = await composer.compose(narrative, {}, bindings, "1")

        bound_slot = next(
            s for s in result.slots
            if s.content_reference == "Block 1 content text"
        )
        assert bound_slot.asset_url == manual_url


class TestHeyGenAdapterPayload:
    @pytest.mark.asyncio
    async def test_presenter_short_payload_structure(self) -> None:
        from integrations.heygen.adapter import HeyGenAdapter

        narrative = _make_narrative_base(num_blocks=2)
        composer = PresenterShortComposer()
        composition = await composer.compose(narrative, {}, [], "1")

        adapter = HeyGenAdapter()
        payload = await adapter.create_payload(composition)

        assert payload["template"] == "presenter_short"
        assert payload["variation"] == "1"
        assert payload["aspect_ratio"] == "9:16"
        assert "scenes" in payload
        assert "avatar" in payload
        assert isinstance(payload["scenes"], list)
        assert len(payload["scenes"]) > 0

    @pytest.mark.asyncio
    async def test_videodoc_payload_structure(self) -> None:
        from integrations.heygen.adapter import HeyGenAdapter

        narrative = _make_narrative_base(
            template_type_id="videodoc_narrated",
            num_blocks=3,
        )
        composer = VideoDocComposer()
        composition = await composer.compose(narrative, {}, [], "1")

        adapter = HeyGenAdapter()
        payload = await adapter.create_payload(composition)

        assert payload["template"] == "videodoc_narrated"
        assert payload["aspect_ratio"] == "16:9"
        assert "scenes" in payload
        assert "narration" in payload
        assert isinstance(payload["scenes"], list)

    @pytest.mark.asyncio
    async def test_payload_scene_fields(self) -> None:
        from integrations.heygen.adapter import HeyGenAdapter

        narrative = _make_narrative_base(num_blocks=2)
        composer = PresenterShortComposer()
        composition = await composer.compose(narrative, {}, [], "2")

        adapter = HeyGenAdapter()
        payload = await adapter.create_payload(composition)

        for scene in payload["scenes"]:
            assert "type" in scene
            assert "duration" in scene
            assert "content" in scene
