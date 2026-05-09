from datetime import datetime
from uuid import UUID
import time

from domain.media_sourcing import (
    VisualBrief,
    SourcingResult,
    SourcingOutcome,
    MediaCandidate,
    MediaType,
)
from domain.media_sourcing.adapters import ArchiveMediaAdapter


class ArchiveMediaSourceAdapter(ArchiveMediaAdapter):
    def __init__(self, base_url: str = "", api_key: str = ""):
        self.base_url = base_url
        self.api_key = api_key

    async def search(
        self,
        brief: VisualBrief,
        production_id: UUID,
        max_results: int = 10,
    ) -> SourcingResult:
        start_time = time.time()

        try:
            filters = self._build_filters_from_brief(brief)
            candidates = await self._query_archive(filters, max_results)

            return SourcingResult(
                outcome=SourcingOutcome.SUCCESS,
                candidates=candidates,
                provider="archive_media",
                duration_ms=(time.time() - start_time) * 1000,
                query_parameters=filters,
            )

        except TimeoutError:
            return SourcingResult(
                outcome=SourcingOutcome.TIMEOUT,
                error_message="Archive timeout",
                provider="archive_media",
                duration_ms=(time.time() - start_time) * 1000,
            )
        except Exception as e:
            return SourcingResult(
                outcome=SourcingOutcome.PROVIDER_ERROR,
                error_message=str(e),
                provider="archive_media",
                duration_ms=(time.time() - start_time) * 1000,
            )

    async def get_asset(self, external_id: str) -> SourcingResult:
        start_time = time.time()

        try:
            asset = await self._fetch_asset_by_id(external_id)
            if asset:
                return SourcingResult(
                    outcome=SourcingOutcome.SUCCESS,
                    candidates=[asset],
                    provider="archive_media",
                    duration_ms=(time.time() - start_time) * 1000,
                )
            return SourcingResult(
                outcome=SourcingOutcome.NO_RESULTS,
                error_message=f"Archive asset {external_id} not found",
                provider="archive_media",
                duration_ms=(time.time() - start_time) * 1000,
            )
        except Exception as e:
            return SourcingResult(
                outcome=SourcingOutcome.PROVIDER_ERROR,
                error_message=str(e),
                provider="archive_media",
                duration_ms=(time.time() - start_time) * 1000,
            )

    def _build_filters_from_brief(self, brief: VisualBrief) -> dict:
        filters = {
            "tags": [],
            "date_range": None,
            "location": None,
        }

        if brief.tema:
            filters["tags"].append(brief.tema)
        if brief.contexto_geografico_cultural:
            filters["location"] = brief.contexto_geografico_cultural
        if brief.periodo:
            filters["date_range"] = brief.periodo

        return filters

    async def _query_archive(self, filters: dict, max_results: int) -> list[MediaCandidate]:
        return []

    async def _fetch_asset_by_id(self, external_id: str) -> MediaCandidate | None:
        return None


archive_media_adapter = ArchiveMediaSourceAdapter()