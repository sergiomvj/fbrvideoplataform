from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class ReviewQueueItem:
    id: UUID = field(default_factory=uuid4)
    production_id: UUID = field(default_factory=uuid4)
    scene_id: UUID = field(default_factory=uuid4)
    asset_id: UUID = field(default_factory=uuid4)
    status: str = "pending"
    score: float = 0.0
    rationale: str = ""
    scene_index: int = 0
    scene_label: str = ""
    asset_url: str = ""
    asset_type: str = ""
    source: str = ""
    preview_url: str = ""
    brief_data: dict = field(default_factory=dict)
    candidate_data: dict = field(default_factory=dict)
    flags: list[str] = field(default_factory=list)


class ReviewQueue:
    def __init__(self) -> None:
        self._items: dict[UUID, ReviewQueueItem] = {}

    async def add_item(
        self,
        production_id: UUID,
        scene_id: UUID,
        asset_id: UUID,
    ) -> ReviewQueueItem:
        item = ReviewQueueItem(
            production_id=production_id,
            scene_id=scene_id,
            asset_id=asset_id,
        )
        self._items[item.id] = item
        return item

    async def get_pending(self, production_id: UUID) -> list[ReviewQueueItem]:
        return [
            i for i in self._items.values()
            if i.production_id == production_id and i.status == "pending"
        ]

    async def approve(self, item_id: UUID) -> ReviewQueueItem | None:
        item = self._items.get(item_id)
        if item:
            item.status = "approved"
        return item

    async def reject(self, item_id: UUID) -> ReviewQueueItem | None:
        item = self._items.get(item_id)
        if item:
            item.status = "rejected"
        return item

    async def requery(self, item_id: UUID) -> ReviewQueueItem | None:
        item = self._items.get(item_id)
        if item:
            item.status = "requeried"
        return item


review_queue = ReviewQueue()
