from __future__ import annotations

import json
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
            score=item.score,
            rationale=item.rationale,
            scene_index=item.scene_index,
            scene_label=item.scene_label,
            asset_url=item.asset_url,
            asset_type=item.asset_type,
            source=item.source,
            preview_url=item.preview_url,
            brief_data_json=json.dumps(item.brief_data) if item.brief_data else None,
            candidate_data_json=json.dumps(item.candidate_data) if item.candidate_data else None,
            flags_json=json.dumps(item.flags) if item.flags else None,
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

    async def get_all_for_production(self, production_id: UUID) -> list[ReviewQueueItem]:
        stmt = (
            select(ReviewQueueItemModel)
            .where(ReviewQueueItemModel.production_id == str(production_id))
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
        item.score = model.score or 0.0
        item.rationale = model.rationale or ""
        item.scene_index = model.scene_index or 0
        item.scene_label = model.scene_label or f"Scene {model.scene_index or 0}"
        item.asset_url = model.asset_url or ""
        item.asset_type = model.asset_type or ""
        item.source = model.source or ""
        item.preview_url = model.preview_url or ""
        item.brief_data = json.loads(model.brief_data_json) if model.brief_data_json else {}
        item.candidate_data = json.loads(model.candidate_data_json) if model.candidate_data_json else {}
        item.flags = json.loads(model.flags_json) if model.flags_json else []
        return item
