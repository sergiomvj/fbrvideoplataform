from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class StructuringReason(str, Enum):
    CONTENT_TOO_SHORT = "content_too_short"
    CONTENT_TOO_LONG = "content_too_long"
    INSUFFICIENT_CONTENT = "insufficient_content"
    TEMPLATE_INCOMPATIBLE = "template_incompatible"


@dataclass
class StructuringError(Exception):
    message: str
    template_type_id: str
    reason: StructuringReason
