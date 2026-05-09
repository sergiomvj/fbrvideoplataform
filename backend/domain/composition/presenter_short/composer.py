from __future__ import annotations

from uuid import UUID

from domain.composition.models import CompositionTimeline, TimelineSlot
from domain.human_review.bindings import ManualBinding
from domain.structuring.models import NarrativeBase

MAX_DURATION = 60.0
MAX_SCENES = 5
ASPECT_RATIO = "9:16"
BACKGROUND_URL = "https://assets.synkra.io/backgrounds/institutional_default.jpg"
PRESENTER_URL = "https://assets.synkra.io/avatars/presenter_default.jpg"


class PresenterShortComposer:
    async def compose(
        self,
        narrative_base: NarrativeBase,
        approved_assets: dict[UUID, str],
        manual_bindings: list[ManualBinding],
        variation_id: str = "1",
    ) -> CompositionTimeline:
        binding_map: dict[UUID, ManualBinding] = {b.scene_id: b for b in manual_bindings}

        slots: list[TimelineSlot] = []
        blocks = narrative_base.blocks[:MAX_SCENES]
        remaining_duration = MAX_DURATION
        per_block = min(
            MAX_DURATION / max(len(blocks), 1),
            remaining_duration,
        )

        for block in blocks:
            duration = min(per_block, remaining_duration)
            if duration <= 0:
                break

            asset_url = self._resolve_asset(
                block.scene_index,
                block.id,
                approved_assets,
                binding_map,
            )

            slots.append(TimelineSlot(
                slot_type="presenter",
                duration_seconds=round(duration, 2),
                content_reference=block.text,
                asset_url=asset_url,
            ))

            remaining_duration -= duration

        interleaved: list[TimelineSlot] = []
        bg = TimelineSlot(
            slot_type="background",
            duration_seconds=0.0,
            content_reference="institutional_background",
            asset_url=self._background_for_variation(variation_id),
        )
        for slot in slots:
            interleaved.append(slot)
            interleaved.append(bg)
        slots = interleaved

        slots.append(TimelineSlot(
            slot_type="narration",
            duration_seconds=0.0,
            content_reference="full_script",
            asset_url=None,
        ))

        total = sum(s.duration_seconds for s in slots)
        if total > MAX_DURATION:
            slots = self._cap_durations(slots, MAX_DURATION)
            total = MAX_DURATION

        return CompositionTimeline(
            production_id=narrative_base.production_id,
            template_type_id="presenter_short",
            variation_id=variation_id,
            slots=slots,
            total_duration_seconds=round(total, 2),
        )

    def _resolve_asset(
        self,
        scene_index: int,
        scene_id: UUID,
        approved_assets: dict[UUID, str],
        binding_map: dict[UUID, ManualBinding],
    ) -> str:
        if scene_id in binding_map:
            return binding_map[scene_id].asset_reference
        if scene_id in approved_assets:
            return approved_assets[scene_id]
        return PRESENTER_URL

    def _background_for_variation(self, variation_id: str) -> str:
        if variation_id == "2":
            return "https://assets.synkra.io/backgrounds/dynamic_bg.jpg"
        if variation_id == "3":
            return "https://assets.synkra.io/backgrounds/text_overlay.jpg"
        return BACKGROUND_URL

    def _cap_durations(
        self,
        slots: list[TimelineSlot],
        max_duration: float,
    ) -> list[TimelineSlot]:
        timed_slots = [s for s in slots if s.duration_seconds > 0]
        if not timed_slots:
            return slots
        current = sum(s.duration_seconds for s in timed_slots)
        if current <= max_duration:
            return slots
        scale = max_duration / current
        for s in timed_slots:
            s.duration_seconds = round(s.duration_seconds * scale, 2)
        return slots
