from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from application.events.domain_events import (
    DomainEvent,
    PRODUCTION_HUMAN_REVIEW_REQUIRED,
    PRODUCTION_HUMAN_REVIEW_COMPLETED,
    PRODUCTION_RENDER_COMPLETED,
    PRODUCTION_RENDER_FAILED,
    PRODUCTION_FAILED,
)

_HUMAN_RELEVANT_EVENTS = {
    PRODUCTION_HUMAN_REVIEW_REQUIRED,
    PRODUCTION_HUMAN_REVIEW_COMPLETED,
    PRODUCTION_RENDER_COMPLETED,
    PRODUCTION_RENDER_FAILED,
    PRODUCTION_FAILED,
}

_notifications_store: list[dict[str, Any]] = []

_SEVERITY_MAP: dict[str, str] = {
    PRODUCTION_HUMAN_REVIEW_REQUIRED: "warning",
    PRODUCTION_HUMAN_REVIEW_COMPLETED: "info",
    PRODUCTION_RENDER_COMPLETED: "info",
    PRODUCTION_RENDER_FAILED: "critical",
    PRODUCTION_FAILED: "critical",
}

_TITLE_MAP: dict[str, str] = {
    PRODUCTION_HUMAN_REVIEW_REQUIRED: "Review Required",
    PRODUCTION_HUMAN_REVIEW_COMPLETED: "Review Completed",
    PRODUCTION_RENDER_COMPLETED: "Render Completed",
    PRODUCTION_RENDER_FAILED: "Render Failed",
    PRODUCTION_FAILED: "Production Failed",
}

_MESSAGE_MAP: dict[str, str] = {
    PRODUCTION_HUMAN_REVIEW_REQUIRED: "A production requires human review before proceeding.",
    PRODUCTION_HUMAN_REVIEW_COMPLETED: "Human review has been completed for a production.",
    PRODUCTION_RENDER_COMPLETED: "Production render has completed successfully.",
    PRODUCTION_RENDER_FAILED: "Production render has failed and needs attention.",
    PRODUCTION_FAILED: "Production has failed and requires investigation.",
}


@dataclass(frozen=True)
class FBRClickNotification:
    channel: str
    title: str
    message: str
    severity: str
    production_id: str | None


class NotificationMapper:
    def map_event(self, event: DomainEvent) -> FBRClickNotification | None:
        if event.event_type not in _HUMAN_RELEVANT_EVENTS:
            return None

        notification = FBRClickNotification(
            channel="fbr_click",
            title=_TITLE_MAP[event.event_type],
            message=_MESSAGE_MAP[event.event_type],
            severity=_SEVERITY_MAP[event.event_type],
            production_id=str(event.production_id) if event.production_id else None,
        )
        _notifications_store.append(
            {
                "channel": notification.channel,
                "title": notification.title,
                "message": notification.message,
                "severity": notification.severity,
                "production_id": notification.production_id,
            }
        )
        return notification
