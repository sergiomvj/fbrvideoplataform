from uuid import UUID
from typing import Optional

from domain.visual_planning.models import VisualBrief
from domain.media_sourcing import (
    MediaSourceAdapter,
    MediaSourceType,
    SourcingResult,
    SourcingOutcome,
)
from domain.audit import audit_service, AuditEventType
from infrastructure.logging import get_logger, LoggingContext

logger = get_logger(__name__)


class MediaSourcingService:
    def __init__(self):
        self._adapters: dict[MediaSourceType, MediaSourceAdapter] = {}

    def register_adapter(self, adapter: MediaSourceAdapter) -> None:
        self._adapters[adapter.source_type] = adapter
        logger.info("media_adapter_registered", source_type=adapter.source_type.value)

    def get_adapter(self, source_type: MediaSourceType) -> Optional[MediaSourceAdapter]:
        return self._adapters.get(source_type)

    async def source_candidates(
        self,
        brief: VisualBrief,
        production_id: UUID,
        source_types: list[MediaSourceType] | None = None,
        max_results_per_source: int = 10,
    ) -> list[SourcingResult]:
        results: list[SourcingResult] = []

        if source_types is None:
            source_types = list(MediaSourceType)

        with LoggingContext(production_id=production_id.hex, scene_id=brief.scene_id.hex):
            for source_type in source_types:
                adapter = self.get_adapter(source_type)
                if not adapter:
                    logger.warning("adapter_not_found", source_type=source_type.value)
                    continue

                logger.info("sourcing_started", source_type=source_type.value)

                result = await adapter.search(
                    brief=brief,
                    production_id=production_id,
                    max_results=max_results_per_source,
                )

                self._emit_audit_event(
                    production_id=production_id,
                    brief_id=brief.id,
                    source_type=source_type.value,
                    result=result,
                )

                logger.info(
                    "sourcing_completed",
                    source_type=source_type.value,
                    outcome=result.outcome.value,
                    candidate_count=len(result.candidates),
                    duration_ms=result.duration_ms,
                )

                results.append(result)

        return results

    async def get_asset_by_source(
        self,
        source_type: MediaSourceType,
        external_id: str,
        production_id: UUID,
    ) -> Optional[SourcingResult]:
        adapter = self.get_adapter(source_type)
        if not adapter:
            logger.warning("adapter_not_found", source_type=source_type.value)
            return None

        with LoggingContext(production_id=production_id.hex):
            logger.info("fetching_asset", source_type=source_type.value, external_id=external_id)
            result = await adapter.get_asset(external_id)

            if result.is_success and result.candidates:
                logger.info("asset_fetched", source_type=source_type.value, external_id=external_id)
            else:
                logger.warning(
                    "asset_fetch_failed",
                    source_type=source_type.value,
                    external_id=external_id,
                    outcome=result.outcome.value,
                )

            return result

    def _emit_audit_event(
        self,
        production_id: UUID,
        brief_id: UUID,
        source_type: str,
        result: SourcingResult,
    ) -> None:
        audit_service.emit(
            event_type=AuditEventType.ASSET_UPLOADED,
            entity_type="media_sourcing",
            entity_id=f"{source_type}:{brief_id.hex}",
            before_state=None,
            after_state={
                "outcome": result.outcome.value,
                "candidate_count": len(result.candidates),
                "duration_ms": result.duration_ms,
            },
            metadata={
                "source_type": source_type,
                "error": result.error_message,
            },
        )


media_sourcing_service = MediaSourcingService()