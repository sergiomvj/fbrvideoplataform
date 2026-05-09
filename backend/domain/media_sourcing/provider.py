from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum


class ProviderType(str, Enum):
    STOCK_IMAGE = "stock_image"
    STOCK_VIDEO = "stock_video"
    ARCHIVE = "archive"
    CUSTOM = "custom"


class ProviderSourceType(str, Enum):
    STOCK_AUTOMATIC = "stock_automatic"
    ARCHIVE_INTERNAL = "archive_internal"
    MANUAL_SELECTED = "manual_selected"


class ProviderStatus(str, Enum):
    ACTIVE = "active"
    DISABLED = "disabled"
    MAINTENANCE = "maintenance"
    ERROR = "error"


@dataclass
class MediaProvider:
    id: UUID = field(default_factory=uuid4)
    provider_key: str = ""
    provider_type: ProviderType = ProviderType.STOCK_IMAGE
    source_type: ProviderSourceType = ProviderSourceType.STOCK_AUTOMATIC
    status: ProviderStatus = ProviderStatus.ACTIVE

    display_name: str = ""
    description: str = ""

    auth_config: dict = field(default_factory=dict)
    operational_config: dict = field(default_factory=dict)

    base_url: str = ""
    api_version: str = "v1"

    rate_limit_per_minute: int = 60
    timeout_seconds: int = 30

    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    disabled_at: datetime | None = None

    metadata: dict = field(default_factory=dict)

    def enable(self) -> None:
        self.status = ProviderStatus.ACTIVE
        self.disabled_at = None
        self.updated_at = datetime.utcnow()

    def disable(self) -> None:
        self.status = ProviderStatus.DISABLED
        self.disabled_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def is_active(self) -> bool:
        return self.status == ProviderStatus.ACTIVE

    def to_dict(self) -> dict:
        return {
            "id": self.id.hex,
            "provider_key": self.provider_key,
            "provider_type": self.provider_type.value,
            "source_type": self.source_type.value,
            "status": self.status.value,
            "display_name": self.display_name,
            "description": self.description,
            "base_url": self.base_url,
            "api_version": self.api_version,
            "rate_limit_per_minute": self.rate_limit_per_minute,
            "timeout_seconds": self.timeout_seconds,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "disabled_at": self.disabled_at.isoformat() if self.disabled_at else None,
        }


class MediaProviderRegistry:
    def __init__(self):
        self._providers: dict[UUID, MediaProvider] = {}
        self._providers_by_key: dict[str, MediaProvider] = {}

    def register(self, provider: MediaProvider) -> MediaProvider:
        self._providers[provider.id] = provider
        self._providers_by_key[provider.provider_key] = provider
        return provider

    def get(self, provider_id: UUID) -> MediaProvider | None:
        return self._providers.get(provider_id)

    def get_by_key(self, provider_key: str) -> MediaProvider | None:
        return self._providers_by_key.get(provider_key)

    def list_all(self) -> list[MediaProvider]:
        return list(self._providers.values())

    def list_active(self) -> list[MediaProvider]:
        return [p for p in self._providers.values() if p.is_active()]

    def list_by_type(self, provider_type: ProviderType) -> list[MediaProvider]:
        return [p for p in self._providers.values() if p.provider_type == provider_type]

    def list_by_source_type(self, source_type: ProviderSourceType) -> list[MediaProvider]:
        return [p for p in self._providers.values() if p.source_type == source_type]

    def update(self, provider_id: UUID, **kwargs) -> MediaProvider | None:
        provider = self._providers.get(provider_id)
        if not provider:
            return None

        for key, value in kwargs.items():
            if hasattr(provider, key):
                setattr(provider, key, value)
        provider.updated_at = datetime.utcnow()

        return provider

    def enable(self, provider_id: UUID) -> MediaProvider | None:
        provider = self._providers.get(provider_id)
        if provider:
            provider.enable()
        return provider

    def disable(self, provider_id: UUID) -> MediaProvider | None:
        provider = self._providers.get(provider_id)
        if provider:
            provider.disable()
        return provider

    def unregister(self, provider_id: UUID) -> bool:
        provider = self._providers.pop(provider_id, None)
        if provider:
            self._providers_by_key.pop(provider.provider_key, None)
            return True
        return False


provider_registry = MediaProviderRegistry()