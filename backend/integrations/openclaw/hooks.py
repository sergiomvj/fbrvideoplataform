from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from application.events.domain_events import (
    DomainEvent,
    PRODUCTION_CREATED,
    PRODUCTION_STRUCTURED,
    PRODUCTION_VISUAL_PLANNED,
    PRODUCTION_MEDIA_SOURCED,
    PRODUCTION_CONTEXT_VERIFIED,
    PRODUCTION_HUMAN_REVIEW_REQUIRED,
    PRODUCTION_HUMAN_REVIEW_COMPLETED,
    PRODUCTION_COMPOSED,
    PRODUCTION_RENDER_SUBMITTED,
    PRODUCTION_RENDER_COMPLETED,
    PRODUCTION_RENDER_FAILED,
    PRODUCTION_FAILED,
)

_webhook_log: list[dict[str, Any]] = []

_EVENT_SUMMARY_MAP: dict[str, str] = {
    PRODUCTION_CREATED: "Production created",
    PRODUCTION_STRUCTURED: "Production structured",
    PRODUCTION_VISUAL_PLANNED: "Visual planning completed",
    PRODUCTION_MEDIA_SOURCED: "Media sourced",
    PRODUCTION_CONTEXT_VERIFIED: "Context verified",
    PRODUCTION_HUMAN_REVIEW_REQUIRED: "Human review required",
    PRODUCTION_HUMAN_REVIEW_COMPLETED: "Human review completed",
    PRODUCTION_COMPOSED: "Production composed",
    PRODUCTION_RENDER_SUBMITTED: "Render submitted",
    PRODUCTION_RENDER_COMPLETED: "Render completed",
    PRODUCTION_RENDER_FAILED: "Render failed",
    PRODUCTION_FAILED: "Production failed",
}

_ACTION_MAP: dict[str, str] = {
    PRODUCTION_HUMAN_REVIEW_REQUIRED: "assign_reviewer",
    PRODUCTION_RENDER_FAILED: "retry_or_investigate",
    PRODUCTION_FAILED: "investigate_failure",
    PRODUCTION_RENDER_COMPLETED: "notify_stakeholders",
}


@dataclass(frozen=True)
class OpenClawWebhookPayload:
    event_type: str
    production_id: str | None
    summary: str
    suggested_action: str


def create_webhook_payload(event: DomainEvent) -> OpenClawWebhookPayload:
    summary = _EVENT_SUMMARY_MAP.get(event.event_type, event.event_type)
    suggested_action = _ACTION_MAP.get(event.event_type, "none")
    payload = OpenClawWebhookPayload(
        event_type=event.event_type,
        production_id=str(event.production_id) if event.production_id else None,
        summary=summary,
        suggested_action=suggested_action,
    )
    _webhook_log.append(
        {
            "event_type": payload.event_type,
            "production_id": payload.production_id,
            "summary": payload.summary,
            "suggested_action": payload.suggested_action,
        }
    )
    return payload


async def send_to_openclaw(event: DomainEvent) -> None:
    payload = create_webhook_payload(event)
