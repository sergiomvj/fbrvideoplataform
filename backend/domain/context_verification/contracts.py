from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID, uuid4
from datetime import datetime


class OperationalDecision(str, Enum):
    AUTO_APPROVED = "auto_approved"
    REVIEW_REQUIRED = "review_required"
    REQUERY_NEEDED = "requery_needed"


class VerificationFlag(str, Enum):
    THEME_MISMATCH = "theme_mismatch"
    SCENE_MISMATCH = "scene_mismatch"
    GEOGRAPHIC_MISMATCH = "geographic_mismatch"
    TEMPORAL_MISMATCH = "temporal_mismatch"
    EDITORIAL_MISMATCH = "editorial_mismatch"
    VISUAL_INADEQUATE = "visual_inadequate"
    CONFLICT_DETECTED = "conflict_detected"
    AMBIGUITY_DETECTED = "ambiguity_detected"


@dataclass
class ScoreBreakdown:
    theme_relevance: float = 0.0
    scene_alignment: float = 0.0
    geographic_coherence: float = 0.0
    temporal_coherence: float = 0.0
    editorial_coherence: float = 0.0
    visual_adequacy: float = 0.0
    conflict_absence: float = 0.0

    def to_dict(self) -> dict:
        return {
            "theme_relevance": self.theme_relevance,
            "scene_alignment": self.scene_alignment,
            "geographic_coherence": self.geographic_coherence,
            "temporal_coherence": self.temporal_coherence,
            "editorial_coherence": self.editorial_coherence,
            "visual_adequacy": self.visual_adequacy,
            "conflict_absence": self.conflict_absence,
        }


@dataclass
class VerificationResult:
    id: UUID = field(default_factory=uuid4)
    candidate_id: UUID = field(default_factory=uuid4)
    brief_id: UUID = field(default_factory=uuid4)
    production_id: UUID = field(default_factory=uuid4)

    score: float = 0.0
    breakdown: ScoreBreakdown = field(default_factory=ScoreBreakdown)
    flags: list[VerificationFlag] = field(default_factory=list)
    decision: OperationalDecision = OperationalDecision.REQUERY_NEEDED

    rationale: str = ""
    details: dict = field(default_factory=dict)

    checked_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        self._apply_threshold_rules()

    def _apply_threshold_rules(self):
        if self.score >= 90.0:
            self.decision = OperationalDecision.AUTO_APPROVED
        elif self.score >= 60.0:
            self.decision = OperationalDecision.REVIEW_REQUIRED
        else:
            self.decision = OperationalDecision.REQUERY_NEEDED

        if self.score < 90.0 and len(self.flags) >= 3:
            self.decision = OperationalDecision.REVIEW_REQUIRED

    @property
    def requires_requery(self) -> bool:
        return self.decision == OperationalDecision.REQUERY_NEEDED

    @property
    def requires_review(self) -> bool:
        return self.decision == OperationalDecision.REVIEW_REQUIRED

    @property
    def is_auto_approved(self) -> bool:
        return self.decision == OperationalDecision.AUTO_APPROVED

    def to_dict(self) -> dict:
        return {
            "id": self.id.hex,
            "candidate_id": self.candidate_id.hex,
            "brief_id": self.brief_id.hex,
            "production_id": self.production_id.hex,
            "score": self.score,
            "breakdown": self.breakdown.to_dict(),
            "flags": [f.value for f in self.flags],
            "decision": self.decision.value,
            "rationale": self.rationale,
            "details": self.details,
            "checked_at": self.checked_at.isoformat(),
        }