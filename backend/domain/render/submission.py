from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4
from typing import Optional


class SubmissionStatus(str, Enum):
    PENDING = "pending"
    VALIDATING = "validating"
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class FailureType(str, Enum):
    VALIDATION_ERROR = "validation_error"
    PROVIDER_SUBMISSION_ERROR = "provider_submission_error"
    PROVIDER_API_ERROR = "provider_api_error"
    TIMEOUT = "timeout"
    AUTH_ERROR = "auth_error"
    RATE_LIMITED = "rate_limited"
    UNKNOWN = "unknown"


class SubmissionOutcome(str, Enum):
    SUCCESS = "success"
    VALIDATION_FAILED = "validation_failed"
    SUBMISSION_FAILED = "submission_failed"
    PROVIDER_ERROR = "provider_error"


@dataclass
class SubmissionPayload:
    production_id: UUID
    composition_data: dict
    output_settings: dict = field(default_factory=dict)
    callback_url: Optional[str] = None
    idempotency_key: str = ""

    def to_provider_format(self, provider: str) -> dict:
        if provider == "heygen":
            return self._to_heygen_format()
        return self._to_generic_format()

    def _to_heygen_format(self) -> dict:
        return {
            "video_config": self.output_settings.get("video_config", {}),
            "scene_data": self.composition_data.get("scenes", []),
            "callback_url": self.callback_url,
        }

    def _to_generic_format(self) -> dict:
        return {
            "production_id": self.production_id.hex,
            "composition": self.composition_data,
            "output": self.output_settings,
        }


@dataclass
class SubmissionResult:
    outcome: SubmissionOutcome
    submission_id: UUID = field(default_factory=uuid4)
    external_job_id: Optional[str] = None
    error_message: Optional[str] = None
    failure_type: Optional[FailureType] = None
    validation_errors: list[str] = field(default_factory=list)
    provider_response: dict = field(default_factory=dict)
    submitted_at: Optional[datetime] = None
    duration_ms: float = 0.0

    @property
    def is_success(self) -> bool:
        return self.outcome == SubmissionOutcome.SUCCESS

    @property
    def is_retryable(self) -> bool:
        if self.outcome == SubmissionOutcome.VALIDATION_FAILED:
            return False
        if self.failure_type == FailureType.AUTH_ERROR:
            return False
        return True


@dataclass
class ProviderJobState:
    external_job_id: str
    provider: str
    status: str
    progress: float = 0.0
    message: Optional[str] = None
    result_url: Optional[str] = None
    error: Optional[str] = None
    last_polled_at: Optional[datetime] = None
    webhook_received_at: Optional[datetime] = None


@dataclass
class RenderSubmissionContract:
    submission_id: UUID
    production_id: UUID
    provider: str
    payload: SubmissionPayload
    status: SubmissionStatus
    result: Optional[SubmissionResult] = None
    job_states: list[ProviderJobState] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "submission_id": self.submission_id.hex,
            "production_id": self.production_id.hex,
            "provider": self.provider,
            "status": self.status.value,
            "outcome": self.result.outcome.value if self.result else None,
            "external_job_id": self.result.external_job_id if self.result else None,
            "error": self.result.error_message if self.result else None,
            "failure_type": self.result.failure_type.value if self.result and self.result.failure_type else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }