from uuid import UUID
from typing import Optional

from domain.visual_planning.models import VisualBrief
from domain.media_sourcing import (
    MediaSourceAdapter,
    MediaSourceType,
    MediaSourceType,
    SourcingResult,
    SourcingOutcome,
    ProviderSourceType,
    provider_registry,
)
from domain.audit import audit_service, AuditEventType
from infrastructure.logging import get_logger, LoggingContext

logger = get_logger(__name__)


class MediaSourcingService:
    def __init__(self):
        self._adapters: dict[MediaSourceType, MediaSourceAdapter] = {}
        self._provider_registry = provider_registry

    def register_adapter(self, adapter: MediaSourceAdapter) -> None:
        self._adapters[adapter.source_type] = adapter
        logger.info("media_adapter_registered", source_type=adapter.source_type.value)

    def get_adapter(self, source_type: MediaSourceType) -> Optional[MediaSourceAdapter]:
        return self._adapters.get(source_type)

    def resolve_active_providers(
        self,
        source_types: list[MediaSourceType] | None = None,
    ) -> list:
        active_providers = self._provider_registry.list_active()
        if source_types:
            source_type_values = [st.value for st in source_types]
            active_providers = [
                p for p in active_providers
                if p.source_type.value in source_type_values
            ]
        return active_providers

    async def source_candidates(
        self,
        brief: VisualBrief,
        production_id: UUID,
        source_types: list[MediaSourceType] | None = None,
        max_results_per_source: int = 10,
    ) -> list[SourcingResult]:
        results: list[SourcingResult] = []

        providers = self.resolve_active_providers(source_types)

        with LoggingContext(production_id=production_id.hex, scene_id=brief.scene_id.hex):
            for provider in providers:
                adapter = self.get_adapter(provider.source_type)
                if not adapter:
                    logger.warning(
                        "adapter_not_found",
                        provider_key=provider.provider_key,
                        source_type=provider.source_type.value,
                    )
                    continue

                logger.info(
                    "sourcing_started",
                    provider_key=provider.provider_key,
                    source_type=provider.source_type.value,
                )

                result = await adapter.search(
                    brief=brief,
                    production_id=production_id,
                    max_results=max_results_per_source,
                )

                self._emit_audit_event(
                    production_id=production_id,
                    brief_id=brief.id,
                    source_type=provider.source_type.value,
                    provider_key=provider.provider_key,
                    result=result,
                )

                logger.info(
                    "sourcing_completed",
                    provider_key=provider.provider_key,
                    source_type=provider.source_type.value,
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
        provider_key: str = "",
    ) -> Optional[SourcingResult]:
        adapter = self.get_adapter(source_type)
        if not adapter:
            logger.warning("adapter_not_found", source_type=source_type.value)
            return None

        with LoggingContext(production_id=production_id.hex):
            logger.info(
                "fetching_asset",
                provider_key=provider_key,
                source_type=source_type.value,
                external_id=external_id,
            )
            result = await adapter.get_asset(external_id)

            if result.is_success and result.candidates:
                logger.info(
                    "asset_fetched",
                    provider_key=provider_key,
                    source_type=source_type.value,
                    external_id=external_id,
                )
            else:
                logger.warning(
                    "asset_fetch_failed",
                    provider_key=provider_key,
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
        provider_key: str = "",
        result: SourcingResult | None = None,
    ) -> None:
        audit_service.emit(
            event_type=AuditEventType.ASSET_UPLOADED,
            entity_type="media_sourcing",
            entity_id=f"{source_type}:{brief_id.hex}",
            before_state=None,
            after_state={
                "outcome": result.outcome.value if result else "unknown",
                "candidate_count": len(result.candidates) if result else 0,
                "duration_ms": result.duration_ms if result else 0,
            },
            metadata={
                "source_type": source_type,
                "provider_key": provider_key,
                "error": result.error_message if result and result.error_message else None,
            },
        )


media_sourcing_service = MediaSourcingService()