from datetime import datetime
from enum import Enum
from typing import Any
from pydantic import BaseModel


class AuditEventType(str, Enum):
    PRODUCTION_CREATED = "production.created"
    PRODUCTION_STATE_CHANGED = "production.state_changed"
    SCENE_CREATED = "scene.created"
    SCENE_STATE_CHANGED = "scene.state_changed"
    ASSET_UPLOADED = "asset.uploaded"
    ASSET_PROCESSED = "asset.processed"
    RENDER_JOB_STARTED = "render_job.started"
    RENDER_JOB_COMPLETED = "render_job.completed"
    RENDER_JOB_FAILED = "render_job.failed"
    DECISION_AUTO_APPROVED = "decision.auto_approved"
    DECISION_MANUAL_REVIEW = "decision.manual_review"
    DECISION_REJECTED = "decision.rejected"
    CONTEXT_VERIFICATION_PASSED = "context_verification.passed"
    CONTEXT_VERIFICATION_FAILED = "context_verification.failed"
    HUMAN_REVIEW_COMPLETED = "human_review.completed"


class AuditEvent(BaseModel):
    event_type: AuditEventType
    timestamp: datetime = datetime.utcnow()
    actor_id: str | None = None
    actor_type: str = "system"
    entity_type: str
    entity_id: str
    before_state: dict[str, Any] | None = None
    after_state: dict[str, Any] | None = None
    metadata: dict[str, Any] = {}

    class Config:
        use_enum_values = True


def log_audit_event(
    event_type: AuditEventType,
    entity_type: str,
    entity_id: str,
    actor_id: str | None = None,
    actor_type: str = "system",
    before_state: dict[str, Any] | None = None,
    after_state: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
) -> AuditEvent:
    event = AuditEvent(
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        actor_id=actor_id,
        actor_type=actor_type,
        before_state=before_state,
        after_state=after_state,
        metadata=metadata or {},
    )
    return event