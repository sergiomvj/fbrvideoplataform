from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID, uuid4


class NarrativeRole(str, Enum):
    OPENING = "opening"
    DEVELOPMENT = "development"
    CLIMAX = "climax"
    CLOSING = "closing"
    TRANSITION = "transition"
    CONTEXT = "context"


@dataclass(frozen=True)
class NarrativeBlock:
    id: UUID = field(default_factory=uuid4)
    role: NarrativeRole = NarrativeRole.DEVELOPMENT
    text: str = ""
    estimated_duration_seconds: float = 0.0
    scene_index: int = 0


@dataclass
class NarrativeBase:
    production_id: UUID
    template_type_id: str
    variation_id: str
    objective: str
    target_duration_seconds: float
    blocks: list[NarrativeBlock] = field(default_factory=list)

    @property
    def total_duration(self) -> float:
        return sum(b.estimated_duration_seconds for b in self.blocks)
