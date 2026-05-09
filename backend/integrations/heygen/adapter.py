from __future__ import annotations

from domain.composition.models import CompositionTimeline
from domain.render.models import RenderJob, RenderJobStatus, render_job_store


class HeyGenAdapter:
    async def create_payload(self, composition: CompositionTimeline) -> dict:
        if composition.template_type_id == "presenter_short":
            return self._presenter_short_payload(composition)
        return self._videodoc_payload(composition)

    async def submit_render_job(
        self,
        composition: CompositionTimeline,
        production_id: str,
    ) -> RenderJob:
        job = RenderJob(
            production_id=composition.production_id,
            composition_id=composition.id,
            provider="heygen",
            status=RenderJobStatus.QUEUED,
        )
        await render_job_store.add(job)
        return job

    def _presenter_short_payload(self, composition: CompositionTimeline) -> dict:
        scenes = []
        for slot in composition.slots:
            scenes.append({
                "type": slot.slot_type,
                "duration": slot.duration_seconds,
                "content": slot.content_reference,
                "asset_url": slot.asset_url,
            })
        return {
            "template": "presenter_short",
            "variation": composition.variation_id,
            "aspect_ratio": "9:16",
            "total_duration": composition.total_duration_seconds,
            "scenes": scenes,
            "avatar": {
                "provider": "heygen",
                "preset": "default_presenter",
            },
        }

    def _videodoc_payload(self, composition: CompositionTimeline) -> dict:
        scenes = []
        for slot in composition.slots:
            scenes.append({
                "type": slot.slot_type,
                "duration": slot.duration_seconds,
                "content": slot.content_reference,
                "asset_url": slot.asset_url,
            })
        return {
            "template": "videodoc_narrated",
            "variation": composition.variation_id,
            "aspect_ratio": "16:9",
            "total_duration": composition.total_duration_seconds,
            "scenes": scenes,
            "narration": {
                "provider": "heygen",
                "voice_preset": "documentary_default",
            },
        }
