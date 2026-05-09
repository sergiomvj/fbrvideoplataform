import structlog
from typing import Any

from .events import AuditEvent, AuditEventType, log_audit_event

logger = structlog.get_logger("audit")


class AuditService:
    def __init__(self):
        self._logger = logger

    def emit(
        self,
        event_type: AuditEventType,
        entity_type: str,
        entity_id: str,
        actor_id: str | None = None,
        actor_type: str = "system",
        before_state: dict[str, Any] | None = None,
        after_state: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditEvent:
        event = log_audit_event(
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            actor_id=actor_id,
            actor_type=actor_type,
            before_state=before_state,
            after_state=after_state,
            metadata=metadata,
        )

        log_data = {
            "audit_event_type": event.event_type,
            "entity_type": event.entity_type,
            "entity_id": event.entity_id,
            "actor_id": event.actor_id,
            "actor_type": event.actor_type,
            "before_state": event.before_state,
            "after_state": event.after_state,
            **event.metadata,
        }

        self._logger.info("audit_event", **log_data)

        return event


audit_service = AuditService()