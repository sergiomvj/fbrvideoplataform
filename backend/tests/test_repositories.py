import pytest
from uuid import uuid4

from domain.human_review.models import ReviewQueueItem
from domain.composition.models import CompositionTimeline, TimelineSlot
from domain.render.models import RenderJob, RenderJobStatus
from infrastructure.db.review_repository import ReviewRepository
from infrastructure.db.composition_repository import CompositionRepository
from infrastructure.db.render_repository import RenderRepository


class TestReviewRepository:
    @pytest.mark.asyncio
    async def test_save_and_get_pending(self, db_session_factory) -> None:
        production_id = uuid4()
        scene_id = uuid4()
        asset_id = uuid4()
        async with db_session_factory() as session:
            repo = ReviewRepository(session)
            item = ReviewQueueItem(
                production_id=production_id,
                scene_id=scene_id,
                asset_id=asset_id,
            )
            await repo.save_item(item)
            await session.commit()

        async with db_session_factory() as session:
            repo = ReviewRepository(session)
            pending = await repo.get_pending(production_id)
            assert len(pending) == 1
            assert pending[0].production_id == production_id
            assert pending[0].scene_id == scene_id
            assert pending[0].status == "pending"

    @pytest.mark.asyncio
    async def test_update_status_to_approved(self, db_session_factory) -> None:
        production_id = uuid4()
        async with db_session_factory() as session:
            repo = ReviewRepository(session)
            item = ReviewQueueItem(
                production_id=production_id,
                scene_id=uuid4(),
                asset_id=uuid4(),
            )
            await repo.save_item(item)
            await session.commit()
            item_id = item.id

        async with db_session_factory() as session:
            repo = ReviewRepository(session)
            updated = await repo.update_status(item_id, "approved", reviewed_by="user-1")
            await session.commit()
            assert updated is not None
            assert updated.status == "approved"

    @pytest.mark.asyncio
    async def test_update_status_nonexistent_returns_none(self, db_session_factory) -> None:
        async with db_session_factory() as session:
            repo = ReviewRepository(session)
            result = await repo.update_status(uuid4(), "approved")
            assert result is None

    @pytest.mark.asyncio
    async def test_approved_not_in_pending(self, db_session_factory) -> None:
        production_id = uuid4()
        async with db_session_factory() as session:
            repo = ReviewRepository(session)
            item = ReviewQueueItem(
                production_id=production_id,
                scene_id=uuid4(),
                asset_id=uuid4(),
            )
            await repo.save_item(item)
            await session.commit()
            await repo.update_status(item.id, "approved", reviewed_by="user-1")
            await session.commit()

        async with db_session_factory() as session:
            repo = ReviewRepository(session)
            pending = await repo.get_pending(production_id)
            assert len(pending) == 0

    @pytest.mark.asyncio
    async def test_isolated_across_productions(self, db_session_factory) -> None:
        prod_a = uuid4()
        prod_b = uuid4()
        async with db_session_factory() as session:
            repo = ReviewRepository(session)
            await repo.save_item(ReviewQueueItem(production_id=prod_a, scene_id=uuid4(), asset_id=uuid4()))
            await repo.save_item(ReviewQueueItem(production_id=prod_a, scene_id=uuid4(), asset_id=uuid4()))
            await repo.save_item(ReviewQueueItem(production_id=prod_b, scene_id=uuid4(), asset_id=uuid4()))
            await session.commit()

        async with db_session_factory() as session:
            repo = ReviewRepository(session)
            assert len(await repo.get_pending(prod_a)) == 2
            assert len(await repo.get_pending(prod_b)) == 1


class TestCompositionRepository:
    @pytest.mark.asyncio
    async def test_save_and_get_by_production(self, db_session_factory) -> None:
        production_id = uuid4()
        composition = CompositionTimeline(
            production_id=production_id,
            template_type_id="presenter_short",
            variation_id="1",
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
        async with db_session_factory() as session:
            repo = CompositionRepository(session)
            await repo.save(composition)
            await session.commit()

        async with db_session_factory() as session:
            repo = CompositionRepository(session)
            result = await repo.get_by_production(production_id)
            assert result is not None
            assert result.production_id == production_id
            assert result.template_type_id == "presenter_short"
            assert len(result.slots) == 1
            assert result.slots[0].slot_type == "presenter"
            assert result.total_duration_seconds == 10.0

    @pytest.mark.asyncio
    async def test_get_nonexistent_returns_none(self, db_session_factory) -> None:
        async with db_session_factory() as session:
            repo = CompositionRepository(session)
            result = await repo.get_by_production(uuid4())
            assert result is None

    @pytest.mark.asyncio
    async def test_save_upsert(self, db_session_factory) -> None:
        production_id = uuid4()
        comp_a = CompositionTimeline(
            production_id=production_id,
            template_type_id="presenter_short",
            total_duration_seconds=5.0,
        )
        async with db_session_factory() as session:
            repo = CompositionRepository(session)
            await repo.save(comp_a)
            await session.commit()

        comp_b = CompositionTimeline(
            id=comp_a.id,
            production_id=production_id,
            template_type_id="videodoc_narrated",
            total_duration_seconds=15.0,
        )
        async with db_session_factory() as session:
            repo = CompositionRepository(session)
            await repo.save(comp_b)
            await session.commit()

        async with db_session_factory() as session:
            repo = CompositionRepository(session)
            result = await repo.get_by_production(production_id)
            assert result is not None
            assert result.template_type_id == "videodoc_narrated"
            assert result.total_duration_seconds == 15.0


class TestRenderRepository:
    @pytest.mark.asyncio
    async def test_save_and_get_by_production(self, db_session_factory) -> None:
        production_id = uuid4()
        job = RenderJob(
            production_id=production_id,
            composition_id=uuid4(),
            provider="heygen",
        )
        async with db_session_factory() as session:
            repo = RenderRepository(session)
            await repo.save_job(job)
            await session.commit()

        async with db_session_factory() as session:
            repo = RenderRepository(session)
            result = await repo.get_by_production(production_id)
            assert result is not None
            assert result.production_id == production_id
            assert result.provider == "heygen"
            assert result.status == RenderJobStatus.QUEUED

    @pytest.mark.asyncio
    async def test_update_status(self, db_session_factory) -> None:
        production_id = uuid4()
        job = RenderJob(
            production_id=production_id,
            composition_id=uuid4(),
            provider="heygen",
        )
        async with db_session_factory() as session:
            repo = RenderRepository(session)
            await repo.save_job(job)
            await session.commit()

        async with db_session_factory() as session:
            repo = RenderRepository(session)
            updated = await repo.update_status(job.id, RenderJobStatus.PROCESSING)
            await session.commit()
            assert updated is not None
            assert updated.status == RenderJobStatus.PROCESSING

    @pytest.mark.asyncio
    async def test_update_status_failed_with_error(self, db_session_factory) -> None:
        job = RenderJob(
            production_id=uuid4(),
            composition_id=uuid4(),
            provider="heygen",
        )
        async with db_session_factory() as session:
            repo = RenderRepository(session)
            await repo.save_job(job)
            await session.commit()

        async with db_session_factory() as session:
            repo = RenderRepository(session)
            updated = await repo.update_status(job.id, RenderJobStatus.FAILED, error_message="API timeout")
            await session.commit()
            assert updated is not None
            assert updated.status == RenderJobStatus.FAILED
            assert updated.error_message == "API timeout"

    @pytest.mark.asyncio
    async def test_update_nonexistent_returns_none(self, db_session_factory) -> None:
        async with db_session_factory() as session:
            repo = RenderRepository(session)
            result = await repo.update_status(uuid4(), RenderJobStatus.PROCESSING)
            assert result is None

    @pytest.mark.asyncio
    async def test_get_nonexistent_returns_none(self, db_session_factory) -> None:
        async with db_session_factory() as session:
            repo = RenderRepository(session)
            result = await repo.get_by_production(uuid4())
            assert result is None
