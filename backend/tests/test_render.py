import pytest
from uuid import uuid4

from domain.composition.models import CompositionTimeline, TimelineSlot
from domain.render.models import RenderJob, RenderJobStatus, RenderJobStore, render_job_store
from integrations.heygen.adapter import HeyGenAdapter


def _make_composition(
    template_type_id: str = "presenter_short",
    variation_id: str = "1",
) -> CompositionTimeline:
    return CompositionTimeline(
        production_id=uuid4(),
        template_type_id=template_type_id,
        variation_id=variation_id,
        slots=[
            TimelineSlot(
                slot_type="presenter",
                duration_seconds=10.0,
                content_reference="test block",
                asset_url="https://assets.synkra.io/test.jpg",
            ),
        ],
        total_duration_seconds=10.0,
    )


class TestRenderJobCreation:
    @pytest.mark.asyncio
    async def test_submit_creates_queued_job(self) -> None:
        adapter = HeyGenAdapter()
        composition = _make_composition()
        job = await adapter.submit_render_job(composition, str(composition.production_id))

        assert job.id is not None
        assert job.production_id == composition.production_id
        assert job.composition_id == composition.id
        assert job.provider == "heygen"
        assert job.status == RenderJobStatus.QUEUED
        assert job.error_message is None

    @pytest.mark.asyncio
    async def test_job_stored_in_store(self) -> None:
        store = RenderJobStore()
        job = RenderJob(
            production_id=uuid4(),
            composition_id=uuid4(),
            provider="heygen",
        )
        await store.add(job)
        retrieved = await store.get(job.id)
        assert retrieved is not None
        assert retrieved.id == job.id


class TestRenderJobStatusTracking:
    @pytest.mark.asyncio
    async def test_status_transitions(self) -> None:
        store = RenderJobStore()
        job = RenderJob(
            production_id=uuid4(),
            composition_id=uuid4(),
            provider="heygen",
        )
        await store.add(job)

        updated = await store.update_status(job.id, RenderJobStatus.PROCESSING)
        assert updated is not None
        assert updated.status == RenderJobStatus.PROCESSING

        completed = await store.update_status(job.id, RenderJobStatus.COMPLETED)
        assert completed is not None
        assert completed.status == RenderJobStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_failed_status_with_error(self) -> None:
        store = RenderJobStore()
        job = RenderJob(
            production_id=uuid4(),
            composition_id=uuid4(),
            provider="heygen",
        )
        await store.add(job)

        failed = await store.update_status(
            job.id, RenderJobStatus.FAILED, error_message="API timeout"
        )
        assert failed is not None
        assert failed.status == RenderJobStatus.FAILED
        assert failed.error_message == "API timeout"

    @pytest.mark.asyncio
    async def test_get_by_production(self) -> None:
        store = RenderJobStore()
        production_id = uuid4()
        job = RenderJob(
            production_id=production_id,
            composition_id=uuid4(),
            provider="heygen",
        )
        await store.add(job)

        found = await store.get_by_production(production_id)
        assert found is not None
        assert found.id == job.id

    @pytest.mark.asyncio
    async def test_update_nonexistent_returns_none(self) -> None:
        store = RenderJobStore()
        result = await store.update_status(uuid4(), RenderJobStatus.PROCESSING)
        assert result is None


class TestHeyGenPayloadMapping:
    @pytest.mark.asyncio
    async def test_presenter_short_payload(self) -> None:
        adapter = HeyGenAdapter()
        composition = _make_composition("presenter_short", "1")
        payload = await adapter.create_payload(composition)

        assert payload["template"] == "presenter_short"
        assert payload["aspect_ratio"] == "9:16"
        assert payload["total_duration"] == 10.0
        assert len(payload["scenes"]) == 1
        assert payload["scenes"][0]["type"] == "presenter"
        assert payload["avatar"]["provider"] == "heygen"

    @pytest.mark.asyncio
    async def test_videodoc_payload(self) -> None:
        adapter = HeyGenAdapter()
        composition = _make_composition("videodoc_narrated", "2")
        payload = await adapter.create_payload(composition)

        assert payload["template"] == "videodoc_narrated"
        assert payload["aspect_ratio"] == "16:9"
        assert payload["variation"] == "2"
        assert payload["narration"]["provider"] == "heygen"

    @pytest.mark.asyncio
    async def test_presenter_variation_3_payload(self) -> None:
        adapter = HeyGenAdapter()
        composition = _make_composition("presenter_short", "3")
        payload = await adapter.create_payload(composition)

        assert payload["variation"] == "3"
        assert payload["aspect_ratio"] == "9:16"
