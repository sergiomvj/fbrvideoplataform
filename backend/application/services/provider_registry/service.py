from __future__ import annotations

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
        self._repository = None

    def set_repository(self, repository) -> None:
        self._repository = repository

    async def initialize_from_db(self) -> None:
        if not self._repository:
            return

        try:
            db_providers = await self._repository.list_all_providers()
            if db_providers:
                for provider in db_providers:
                    self._registry.register(provider)
                logger.info("providers_loaded_from_db", count=len(db_providers))
            else:
                await self._seed_defaults()
        except Exception as e:
            logger.warning("db_load_failed_fallback_memory", error=str(e))
            self._seed_defaults_sync()

    async def _seed_defaults(self) -> None:
        default_providers = self._get_default_providers()
        for provider in default_providers:
            self._registry.register(provider)
            if self._repository:
                try:
                    await self._repository.save_provider(provider)
                except Exception as e:
                    logger.warning("provider_persist_failed", provider_key=provider.provider_key, error=str(e))
        logger.info("default_providers_initialized", count=len(default_providers))

    def _seed_defaults_sync(self) -> None:
        default_providers = self._get_default_providers()
        for provider in default_providers:
            self._registry.register(provider)
        logger.info("default_providers_initialized_sync", count=len(default_providers))

    def _get_default_providers(self) -> list[MediaProvider]:
        return [
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

        if self._repository:
            try:
                await self._repository.save_provider(provider)
            except Exception as e:
                logger.warning("provider_persist_failed", provider_key=provider_key, error=str(e))

        logger.info(
            "provider_created",
            provider_id=provider.id.hex,
            provider_key=provider_key,
            provider_type=provider_type.value,
        )

        self._emit_audit_event(provider, "created")

        return provider

    async def get_provider(self, provider_id: UUID) -> Optional[MediaProvider]:
        provider = self._registry.get(provider_id)
        if provider:
            return provider
        if self._repository:
            try:
                return await self._repository.get_provider(provider_id)
            except Exception:
                pass
        return None

    async def get_provider_by_key(self, provider_key: str) -> Optional[MediaProvider]:
        provider = self._registry.get_by_key(provider_key)
        if provider:
            return provider
        if self._repository:
            try:
                return await self._repository.get_provider_by_key(provider_key)
            except Exception:
                pass
        return None

    async def list_providers(
        self,
        provider_type: Optional[ProviderType] = None,
        source_type: Optional[ProviderSourceType] = None,
        status: Optional[ProviderStatus] = None,
    ) -> list[MediaProvider]:
        if self._repository:
            try:
                providers = await self._repository.list_providers(
                    provider_type=provider_type,
                    source_type=source_type,
                    status=status,
                )
                if providers:
                    for p in providers:
                        self._registry.register(p)
                    return providers
            except Exception:
                pass
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
        if self._repository:
            try:
                providers = await self._repository.list_active_providers(source_type=source_type)
                if providers:
                    for p in providers:
                        self._registry.register(p)
                    return providers
            except Exception:
                pass
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

        if provider and self._repository:
            try:
                await self._repository.save_provider(provider)
            except Exception as e:
                logger.warning("provider_persist_failed", provider_id=provider_id.hex, error=str(e))

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

        if provider and self._repository:
            try:
                await self._repository.save_provider(provider)
            except Exception as e:
                logger.warning("provider_persist_failed", provider_id=provider_id.hex, error=str(e))

        if provider:
            logger.info("provider_enabled", provider_id=provider_id.hex)
            self._emit_audit_event(provider, "enabled")

        return provider

    async def disable_provider(self, provider_id: UUID) -> Optional[MediaProvider]:
        provider = self._registry.disable(provider_id)

        if provider and self._repository:
            try:
                await self._repository.save_provider(provider)
            except Exception as e:
                logger.warning("provider_persist_failed", provider_id=provider_id.hex, error=str(e))

        if provider:
            logger.info("provider_disabled", provider_id=provider_id.hex)
            self._emit_audit_event(provider, "disabled")

        return provider

    async def delete_provider(self, provider_id: UUID) -> bool:
        provider = self._registry.get(provider_id)
        if not provider:
            return False

        deleted = self._registry.unregister(provider_id)

        if deleted and self._repository:
            try:
                await self._repository.delete_provider(provider_id)
            except Exception as e:
                logger.warning("provider_delete_persist_failed", provider_id=provider_id.hex, error=str(e))

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
