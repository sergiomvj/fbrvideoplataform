from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass
class BriefPlanningError(Exception):
    message: str
    scene_id: UUID | None = None
    reason: str = ""
