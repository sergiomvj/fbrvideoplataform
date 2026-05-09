from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Coroutine
from uuid import UUID
from collections import defaultdict
import asyncio

PRODUCTION_CREATED = "production.created"
PRODUCTION_STRUCTURED = "production.structured"
PRODUCTION_VISUAL_PLANNED = "production.visual_planned"
PRODUCTION_MEDIA_SOURCED = "production.media_sourced"
PRODUCTION_CONTEXT_VERIFIED = "production.context_verified"
PRODUCTION_HUMAN_REVIEW_REQUIRED = "production.human_review_required"
PRODUCTION_HUMAN_REVIEW_COMPLETED = "production.human_review_completed"
PRODUCTION_COMPOSED = "production.composed"
PRODUCTION_RENDER_SUBMITTED = "production.render_submitted"
PRODUCTION_RENDER_COMPLETED = "production.render_completed"
PRODUCTION_RENDER_FAILED = "production.render_failed"
PRODUCTION_FAILED = "production.failed"

Handler = Callable[["DomainEvent"], Coroutine[Any, Any, None]]


@dataclass(frozen=True)
class DomainEvent:
    event_type: str
    production_id: UUID | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = "synkra-backend"


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[Handler]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: Handler) -> None:
        self._subscribers[event_type].append(handler)

    async def emit(self, event: DomainEvent) -> None:
        handlers = self._subscribers.get(event.event_type, [])
        for handler in handlers:
            await handler(event)
