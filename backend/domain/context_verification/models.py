from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class AssetCandidate:
    id: UUID = field(default_factory=uuid4)
    scene_id: UUID = field(default_factory=uuid4)
    source: str = ""
    asset_type: str = ""
    reference: str = ""
    url: str = ""


@dataclass
class VerificationScore:
    asset_id: UUID = field(default_factory=uuid4)
    scene_id: UUID = field(default_factory=uuid4)
    score: float = 0.0
    justification: str = ""
    decision: str = "human_review"


async def verify_asset(candidate: AssetCandidate, brief: str = "") -> VerificationScore:
    return VerificationScore(
        asset_id=candidate.id,
        scene_id=candidate.scene_id,
        score=85.0,
        justification="Stub verification: default score",
        decision="human_review",
    )
