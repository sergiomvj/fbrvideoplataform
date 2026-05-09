from uuid import UUID
from typing import Optional

from domain.media_sourcing import (
    MediaProvider,
    ProviderType,
    ProviderSourceType,
    ProviderStatus,
    provider_registry,
)
from domain.audit import audit_service, AuditEventType
from infrastructure.logging import get_logger, LoggingContext

logger = get_logger(__name__)


class ProviderRegistryService:
    def __init__(self):
        self._registry = provider_registry
        self._initialize_default_providers()

    def _initialize_default_providers(self) -> None:
        if not self._registry.list_all():
            default_providers = [
                MediaProvider(
                    provider_key="pexels",
                    provider_type=ProviderType.STOCK_IMAGE,
                    source_type=ProviderSourceType.STOCK_AUTOMATIC,
                    display_name="Pexels",
                    description="Free stock photos and videos",
                    base_url="https://api.pexels.com/v1",
                    operational_config={"search_endpoint": "/search"},
                ),
                MediaProvider(
                    provider_key="pixabay",
                    provider_type=ProviderType.STOCK_IMAGE,
                    source_type=ProviderSourceType.STOCK_AUTOMATIC,
                    display_name="Pixabay",
                    description="Free images and videos",
                    base_url="https://pixabay.com/api",
                    operational_config={"search_endpoint": ""},
                ),
                MediaProvider(
                    provider_key="archive_internal",
                    provider_type=ProviderType.ARCHIVE,
                    source_type=ProviderSourceType.ARCHIVE_INTERNAL,
                    display_name="Internal Archive",
                    description="Internal media archive",
                    base_url="",
                    operational_config={"storage_path": "/archive"},
                ),
            ]

            for provider in default_providers:
                self._registry.register(provider)

            logger.info("default_providers_initialized", count=len(default_providers))

    async def create_provider(
        self,
        provider_key: str,
        provider_type: ProviderType,
        source_type: ProviderSourceType,
        display_name: str,
        description: str = "",
        base_url: str = "",
        auth_config: Optional[dict] = None,
        operational_config: Optional[dict] = None,
    ) -> MediaProvider:
        provider = MediaProvider(
            provider_key=provider_key,
            provider_type=provider_type,
            source_type=source_type,
            display_name=display_name,
            description=description,
            base_url=base_url,
            auth_config=auth_config or {},
            operational_config=operational_config or {},
        )

        self._registry.register(provider)

        logger.info(
            "provider_created",
            provider_id=provider.id.hex,
            provider_key=provider_key,
            provider_type=provider_type.value,
        )

        self._emit_audit_event(provider, "created")

        return provider

    async def get_provider(self, provider_id: UUID) -> Optional[MediaProvider]:
        return self._registry.get(provider_id)

    async def get_provider_by_key(self, provider_key: str) -> Optional[MediaProvider]:
        return self._registry.get_by_key(provider_key)

    async def list_providers(
        self,
        provider_type: Optional[ProviderType] = None,
        source_type: Optional[ProviderSourceType] = None,
        status: Optional[ProviderStatus] = None,
    ) -> list[MediaProvider]:
        providers = self._registry.list_all()

        if provider_type:
            providers = [p for p in providers if p.provider_type == provider_type]
        if source_type:
            providers = [p for p in providers if p.source_type == source_type]
        if status:
            providers = [p for p in providers if p.status == status]

        return providers

    async def list_active_providers(
        self,
        source_type: Optional[ProviderSourceType] = None,
    ) -> list[MediaProvider]:
        providers = self._registry.list_active()

        if source_type:
            providers = [p for p in providers if p.source_type == source_type]

        return providers

    async def update_provider(
        self,
        provider_id: UUID,
        **kwargs,
    ) -> Optional[MediaProvider]:
        provider = self._registry.update(provider_id, **kwargs)

        if provider:
            logger.info(
                "provider_updated",
                provider_id=provider_id.hex,
                fields=list(kwargs.keys()),
            )
            self._emit_audit_event(provider, "updated")

        return provider

    async def enable_provider(self, provider_id: UUID) -> Optional[MediaProvider]:
        provider = self._registry.enable(provider_id)

        if provider:
            logger.info("provider_enabled", provider_id=provider_id.hex)
            self._emit_audit_event(provider, "enabled")

        return provider

    async def disable_provider(self, provider_id: UUID) -> Optional[MediaProvider]:
        provider = self._registry.disable(provider_id)

        if provider:
            logger.info("provider_disabled", provider_id=provider_id.hex)
            self._emit_audit_event(provider, "disabled")

        return provider

    async def delete_provider(self, provider_id: UUID) -> bool:
        provider = self._registry.get(provider_id)
        if not provider:
            return False

        deleted = self._registry.unregister(provider_id)

        if deleted:
            logger.info("provider_deleted", provider_id=provider_id.hex)
            self._emit_audit_event(provider, "deleted")

        return deleted

    def _emit_audit_event(self, provider: MediaProvider, action: str) -> None:
        audit_service.emit(
            event_type=AuditEventType.ASSET_PROCESSED,
            entity_type="media_provider",
            entity_id=provider.id.hex,
            metadata={
                "action": action,
                "provider_key": provider.provider_key,
                "provider_type": provider.provider_type.value,
                "status": provider.status.value,
            },
        )


provider_registry_service = ProviderRegistryService()