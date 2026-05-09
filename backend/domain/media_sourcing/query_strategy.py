from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum
from typing import Optional


class QueryStrategyType(str, Enum):
    LITERAL = "literal"
    CONTEXTUAL = "contextual"
    BROAD = "broad"
    FALLBACK = "fallback"


class DiagnosticCategory(str, Enum):
    THEME_MISMATCH = "theme_mismatch"
    SCENE_MISMATCH = "scene_mismatch"
    QUALITY_TOO_LOW = "quality_too_low"
    NO_RELEVANT_RESULTS = "no_relevant_results"
    PROVIDER_ERROR = "provider_error"
    TIMEOUT = "timeout"


@dataclass
class QueryStrategy:
    strategy_type: QueryStrategyType = QueryStrategyType.CONTEXTUAL
    keywords: list[str] = field(default_factory=list)
    exclusions: list[str] = field(default_factory=list)
    aspect_ratio: str = "16:9"
    orientation: str = "landscape"
    media_type: str = "any"
    max_results: int = 10

    def to_provider_params(self) -> dict:
        return {
            "keywords": " ".join(self.keywords),
            "exclusions": " ".join(self.exclusions) if self.exclusions else None,
            "aspect_ratio": self.aspect_ratio,
            "orientation": self.orientation,
            "media_type": self.media_type,
            "per_page": self.max_results,
        }


@dataclass
class QueryAttempt:
    id: UUID = field(default_factory=uuid4)
    production_id: UUID = field(default_factory=uuid4)
    scene_id: UUID = field(default_factory=uuid4)
    brief_id: UUID = field(default_factory=uuid4)

    strategy: QueryStrategy = field(default_factory=QueryStrategy)
    provider_key: str = ""

    attempt_number: int = 1

    query_params: dict = field(default_factory=dict)
    candidate_count: int = 0

    diagnostic: Optional[DiagnosticCategory] = None
    diagnostic_details: str = ""

    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    def is_low_confidence(self, min_score_threshold: float = 60.0) -> bool:
        return self.candidate_count == 0 or self.diagnostic is not None

    def to_dict(self) -> dict:
        return {
            "id": self.id.hex,
            "production_id": self.production_id.hex,
            "scene_id": self.scene_id.hex,
            "strategy_type": self.strategy.strategy_type.value,
            "attempt_number": self.attempt_number,
            "query_params": self.query_params,
            "candidate_count": self.candidate_count,
            "diagnostic": self.diagnostic.value if self.diagnostic else None,
            "diagnostic_details": self.diagnostic_details,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


@dataclass
class QueryReformulation:
    original_attempt: QueryAttempt
    reformulated_strategy: QueryStrategy
    reformulation_reason: str

    def to_dict(self) -> dict:
        return {
            "original_attempt_id": self.original_attempt.id.hex,
            "reformulated_strategy": self.reformulated_strategy.to_provider_params(),
            "reason": self.reformulation_reason,
        }