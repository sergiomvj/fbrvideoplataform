from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.human_review.models import ReviewQueueItem
from infrastructure.db.models import ReviewQueueItemModel


class ReviewRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save_item(self, item: ReviewQueueItem) -> ReviewQueueItem:
        model = ReviewQueueItemModel(
            id=str(item.id),
            production_id=str(item.production_id),
            scene_id=str(item.scene_id),
            asset_id=str(item.asset_id) if item.asset_id else None,
            status=item.status,
        )
        self.session.add(model)
        await self.session.flush()
        return item

    async def get_pending(self, production_id: UUID) -> list[ReviewQueueItem]:
        stmt = (
            select(ReviewQueueItemModel)
            .where(
                ReviewQueueItemModel.production_id == str(production_id),
                ReviewQueueItemModel.status == "pending",
            )
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def get_by_id(self, item_id: UUID) -> ReviewQueueItem | None:
        stmt = select(ReviewQueueItemModel).where(
            ReviewQueueItemModel.id == str(item_id)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def update_status(
        self,
        item_id: UUID,
        status: str,
        reviewed_by: str | None = None,
    ) -> ReviewQueueItem | None:
        stmt = select(ReviewQueueItemModel).where(
            ReviewQueueItemModel.id == str(item_id)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        model.status = status
        if reviewed_by:
            model.reviewed_by = reviewed_by
            model.reviewed_at = datetime.now(timezone.utc)
        await self.session.flush()
        return self._to_domain(model)

    def _to_domain(self, model: ReviewQueueItemModel) -> ReviewQueueItem:
        item = ReviewQueueItem.__new__(ReviewQueueItem)
        item.id = UUID(model.id)
        item.production_id = UUID(model.production_id)
        item.scene_id = UUID(model.scene_id)
        item.asset_id = UUID(model.asset_id) if model.asset_id else item.id
        item.status = model.status
        return item
