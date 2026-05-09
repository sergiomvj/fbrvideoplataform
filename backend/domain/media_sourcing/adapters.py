from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from domain.visual_planning.models import VisualBrief
from .contracts import SourcingResult, MediaSourceType


class MediaSourceAdapter(ABC):
    source_type: MediaSourceType

    @abstractmethod
    async def search(
        self,
        brief: VisualBrief,
        production_id: UUID,
        max_results: int = 10,
    ) -> SourcingResult:
        """Search for candidate media based on visual brief."""
        pass

    @abstractmethod
    async def get_asset(self, external_id: str) -> Optional[SourcingResult]:
        """Retrieve specific asset by external ID."""
        pass

    def can_handle(self, source_type: MediaSourceType) -> bool:
        return self.source_type == source_type


class StockMediaAdapter(MediaSourceAdapter):
    source_type = MediaSourceType.STOCK_AUTOMATIC


class ArchiveMediaAdapter(MediaSourceAdapter):
    source_type = MediaSourceType.ARCHIVE_INTERNAL


class ManualSelectionAdapter(MediaSourceAdapter):
    source_type = MediaSourceType.MANUAL_SELECTED