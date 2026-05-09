from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional


class MediaSourceType(str, Enum):
    STOCK_AUTOMATIC = "stock_automatic"
    ARCHIVE_INTERNAL = "archive_internal"
    MANUAL_SELECTED = "manual_selected"


class MediaType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"


class SourcingOutcome(str, Enum):
    SUCCESS = "success"
    PROVIDER_ERROR = "provider_error"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"
    NO_RESULTS = "no_results"


@dataclass
class MediaCandidate:
    id: UUID = field(default_factory=uuid4)
    source_type: MediaSourceType = MediaSourceType.STOCK_AUTOMATIC
    source_provider: str = ""
    external_id: str = ""
    media_type: MediaType = MediaType.IMAGE
    url: str = ""
    thumbnail_url: str = ""
    title: str = ""
    description: str = ""
    duration_seconds: Optional[float] = None
    resolution: Optional[str] = None
    aspect_ratio: Optional[str] = None
    license_type: str = "royalty_free"
    attribution_required: bool = False
    metadata: dict = field(default_factory=dict)
    relevance_score: Optional[float] = None


@dataclass
class SourcingResult:
    outcome: SourcingOutcome
    candidates: list[MediaCandidate] = field(default_factory=list)
    error_message: Optional[str] = None
    provider: str = ""
    duration_ms: float = 0.0
    query_parameters: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    @property
    def is_success(self) -> bool:
        return self.outcome == SourcingOutcome.SUCCESS

    @property
    def is_empty(self) -> bool:
        return self.is_success and len(self.candidates) == 0