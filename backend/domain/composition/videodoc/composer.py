from __future__ import annotations

from uuid import UUID

from domain.composition.models import CompositionTimeline, TimelineSlot
from domain.human_review.bindings import ManualBinding
from domain.structuring.models import NarrativeBase

MAX_DURATION = 180.0
MIN_SCENES = 2
MAX_SCENES = 12
ASPECT_RATIO = "16:9"


class VideoDocComposer:
    async def compose(
        self,
        narrative_base: NarrativeBase,
        approved_assets: dict[UUID, str],
        manual_bindings: list[ManualBinding],
        variation_id: str = "1",
    ) -> CompositionTimeline:
        binding_map: dict[UUID, ManualBinding] = {b.scene_id: b for b in manual_bindings}

        blocks = narrative_base.blocks[:MAX_SCENES]
        if len(blocks) < MIN_SCENES:
            blocks = blocks + [blocks[-1]] if blocks else blocks

        remaining_duration = MAX_DURATION
        per_block = min(
            MAX_DURATION / max(len(blocks), 1),
            remaining_duration,
        )

        slots: list[TimelineSlot] = []

        for block in blocks:
            duration = min(per_block, remaining_duration)
            if duration <= 0:
                break

            asset_url = self._resolve_asset(
                block.id,
                approved_assets,
                binding_map,
            )

            presenter_slot = TimelineSlot(
                slot_type=self._presenter_type_for_variation(variation_id),
                duration_seconds=round(duration, 2),
                content_reference=block.text,
                asset_url=asset_url,
            )
            slots.append(presenter_slot)

            if variation_id != "2":
                broll_url = self._broll_for_variation(variation_id, block.scene_index)
                slots.append(TimelineSlot(
                    slot_type="image" if variation_id == "1" else "video",
                    duration_seconds=0.0,
                    content_reference=f"broll_scene_{block.scene_index}",
                    asset_url=broll_url,
                ))

            remaining_duration -= duration

        slots.append(TimelineSlot(
            slot_type="narration",
            duration_seconds=0.0,
            content_reference="full_narration",
            asset_url=None,
        ))

        total = sum(s.duration_seconds for s in slots)
        if total > MAX_DURATION:
            slots = self._cap_durations(slots, MAX_DURATION)
            total = MAX_DURATION

        return CompositionTimeline(
            production_id=narrative_base.production_id,
            template_type_id="videodoc_narrated",
            variation_id=variation_id,
            slots=slots,
            total_duration_seconds=round(total, 2),
        )

    def _resolve_asset(
        self,
        scene_id: UUID,
        approved_assets: dict[UUID, str],
        binding_map: dict[UUID, ManualBinding],
    ) -> str:
        if scene_id in binding_map:
            return binding_map[scene_id].asset_reference
        if scene_id in approved_assets:
            return approved_assets[scene_id]
        return "https://assets.synkra.io/defaults/videodoc_scene.jpg"

    def _presenter_type_for_variation(self, variation_id: str) -> str:
        if variation_id == "2":
            return "presenter"
        if variation_id == "3":
            return "presenter"
        return "narrator"

    def _broll_for_variation(self, variation_id: str, scene_index: int) -> str:
        if variation_id == "3":
            return f"https://assets.synkra.io/broll/documentary_{scene_index}.mp4"
        return f"https://assets.synkra.io/broll/standard_{scene_index}.jpg"

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
