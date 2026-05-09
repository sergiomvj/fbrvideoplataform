from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum


class RequeryStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    EXHAUSTED = "exhausted"
    STRUCTURAL_FAILURE = "structural_failure"


class ReviewQueueStatus(str, Enum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class RequeryAttempt:
    id: UUID = field(default_factory=uuid4)
    production_id: UUID = field(default_factory=uuid4)
    scene_id: UUID = field(default_factory=uuid4)
    candidate_id: UUID = field(default_factory=uuid4)
    attempt_number: int = 0
    status: RequeryStatus = RequeryStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_attempt_at: datetime | None = None
    max_attempts: int = 3
    failure_reason: str = ""

    def can_retry(self) -> bool:
        return (
            self.status != RequeryStatus.STRUCTURAL_FAILURE
            and self.attempt_number < self.max_attempts
        )

    def increment_attempt(self) -> None:
        self.attempt_number += 1
        self.last_attempt_at = datetime.utcnow()
        if self.attempt_number >= self.max_attempts:
            self.status = RequeryStatus.EXHAUSTED

    def mark_structural_failure(self, reason: str) -> None:
        self.status = RequeryStatus.STRUCTURAL_FAILURE
        self.failure_reason = reason


@dataclass
class ReviewQueueItem:
    id: UUID = field(default_factory=uuid4)
    production_id: UUID = field(default_factory=uuid4)
    scene_id: UUID = field(default_factory=uuid4)
    candidate_id: UUID = field(default_factory=uuid4)
    brief_data: dict = field(default_factory=dict)
    candidate_data: dict = field(default_factory=dict)
    score: float = 0.0
    rationale: str = ""
    flags: list[str] = field(default_factory=list)
    status: ReviewQueueStatus = ReviewQueueStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    reviewed_at: datetime | None = None
    reviewed_by: str | None = None

    def to_display_dict(self) -> dict:
        return {
            "id": self.id.hex,
            "production_id": self.production_id.hex,
            "scene_id": self.scene_id.hex,
            "candidate_id": self.candidate_id.hex,
            "brief": self.brief_data,
            "candidate": self.candidate_data,
            "score": self.score,
            "rationale": self.rationale,
            "flags": self.flags,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "reviewed_by": self.reviewed_by,
        }


class RequeryWorkflow:
    MAX_ATTEMPTS = 3

    def __init__(self):
        self._attempts: dict[UUID, RequeryAttempt] = {}

    def create_attempt(
        self,
        production_id: UUID,
        scene_id: UUID,
        candidate_id: UUID,
    ) -> RequeryAttempt:
        attempt = RequeryAttempt(
            production_id=production_id,
            scene_id=scene_id,
            candidate_id=candidate_id,
            max_attempts=self.MAX_ATTEMPTS,
        )
        self._attempts[attempt.id] = attempt
        return attempt

    def get_attempt(self, attempt_id: UUID) -> RequeryAttempt | None:
        return self._attempts.get(attempt_id)

    def get_active_attempts(self, production_id: UUID) -> list[RequeryAttempt]:
        return [
            a for a in self._attempts.values()
            if a.production_id == production_id
            and a.status in [RequeryStatus.PENDING, RequeryStatus.IN_PROGRESS]
        ]

    def record_retry(self, attempt_id: UUID) -> RequeryAttempt | None:
        attempt = self._attempts.get(attempt_id)
        if attempt and attempt.can_retry():
            attempt.increment_attempt()
            if attempt.attempt_number < attempt.max_attempts:
                attempt.status = RequeryStatus.IN_PROGRESS
            return attempt
        return None

    def mark_failure(self, attempt_id: UUID, reason: str) -> RequeryAttempt | None:
        attempt = self._attempts.get(attempt_id)
        if attempt:
            attempt.mark_structural_failure(reason)
            return attempt
        return None


requery_workflow = RequeryWorkflow()