from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass
class AuditEvent:
    id: UUID = field(default_factory=uuid4)
    event_type: str = ""
    production_id: UUID | None = None
    user_id: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    details: dict = field(default_factory=dict)


_audit_store: list[AuditEvent] = []


async def emit_audit_event(
    event_type: str,
    production_id: UUID | None,
    user_id: str,
    details: dict | None = None,
) -> AuditEvent:
    event = AuditEvent(
        event_type=event_type,
        production_id=production_id,
        user_id=user_id,
        details=details or {},
    )
    _audit_store.append(event)
    return event


async def get_audit_events(production_id: UUID) -> list[AuditEvent]:
    return [e for e in _audit_store if e.production_id == production_id]
