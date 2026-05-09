from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class TimelineSlot:
    slot_type: str = ""
    duration_seconds: float = 0.0
    content_reference: str = ""
    asset_url: str | None = None


@dataclass
class CompositionTimeline:
    id: UUID = field(default_factory=uuid4)
    production_id: UUID = field(default_factory=uuid4)
    template_type_id: str = ""
    variation_id: str = "1"
    slots: list[TimelineSlot] = field(default_factory=list)
    total_duration_seconds: float = 0.0
