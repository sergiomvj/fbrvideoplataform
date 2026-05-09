from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.media_sourcing.provider import (
    MediaProvider,
    ProviderType,
    ProviderSourceType,
    ProviderStatus,
)
from infrastructure.db.models import MediaProviderModel


class ProviderRepository:
    """Repository for media provider persistence."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_provider(self, provider: MediaProvider) -> MediaProvider:
        existing = await self._get_model(provider.id)
        if existing:
            existing.provider_key = provider.provider_key
            existing.provider_type = provider.provider_type.value
            existing.source_type = provider.source_type.value
            existing.status = provider.status.value
            existing.display_name = provider.display_name
            existing.description = provider.description
            existing.base_url = provider.base_url
            existing.api_version = provider.api_version
            existing.auth_config = json.dumps(provider.auth_config)
            existing.operational_config = json.dumps(provider.operational_config)
            existing.rate_limit_per_minute = provider.rate_limit_per_minute
            existing.timeout_seconds = provider.timeout_seconds
            existing.disabled_at = provider.disabled_at
            existing.updated_at = datetime.now(timezone.utc)
        else:
            model = MediaProviderModel(
                id=str(provider.id),
                provider_key=provider.provider_key,
                provider_type=provider.provider_type.value,
                source_type=provider.source_type.value,
                status=provider.status.value,
                display_name=provider.display_name,
                description=provider.description,
                base_url=provider.base_url,
                api_version=provider.api_version,
                auth_config=json.dumps(provider.auth_config),
                operational_config=json.dumps(provider.operational_config),
                rate_limit_per_minute=provider.rate_limit_per_minute,
                timeout_seconds=provider.timeout_seconds,
                disabled_at=provider.disabled_at,
                created_at=provider.created_at,
                updated_at=provider.updated_at,
            )
            self.session.add(model)

        await self.session.flush()
        return provider

    async def get_provider(self, provider_id: UUID) -> Optional[MediaProvider]:
        model = await self._get_model(provider_id)
        if model is None:
            return None
        return self._to_domain(model)

    async def get_provider_by_name(self, organization_id: UUID, name: str) -> Optional[MediaProvider]:
        stmt = select(MediaProviderModel).where(
            MediaProviderModel.display_name == name,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def get_provider_by_key(self, provider_key: str) -> Optional[MediaProvider]:
        stmt = select(MediaProviderModel).where(
            MediaProviderModel.provider_key == provider_key,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def list_active_providers(self, organization_id: UUID) -> List[MediaProvider]:
        stmt = select(MediaProviderModel).where(
            MediaProviderModel.status == ProviderStatus.ACTIVE.value,
        )
        result = await self.session.execute(stmt)
        return [self._to_domain(m) for m in result.scalars().all()]

    async def list_all_providers(self) -> List[MediaProvider]:
        stmt = select(MediaProviderModel)
        result = await self.session.execute(stmt)
        return [self._to_domain(m) for m in result.scalars().all()]

    async def list_providers_by_type(self, organization_id: UUID, provider_type: str) -> List[MediaProvider]:
        stmt = select(MediaProviderModel).where(
            MediaProviderModel.provider_type == provider_type,
        )
        result = await self.session.execute(stmt)
        return [self._to_domain(m) for m in result.scalars().all()]

    async def deactivate_provider(self, provider_id: UUID) -> bool:
        model = await self._get_model(provider_id)
        if model is None:
            return False
        model.status = ProviderStatus.DISABLED.value
        model.disabled_at = datetime.now(timezone.utc)
        model.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        return True

    async def delete_provider(self, provider_id: UUID) -> bool:
        model = await self._get_model(provider_id)
        if model is None:
            return False
        await self.session.delete(model)
        await self.session.flush()
        return True

    async def _get_model(self, provider_id: UUID) -> Optional[MediaProviderModel]:
        stmt = select(MediaProviderModel).where(
            MediaProviderModel.id == str(provider_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    def _to_domain(self, model: MediaProviderModel) -> MediaProvider:
        return MediaProvider(
            id=UUID(model.id),
            provider_key=model.provider_key,
            provider_type=ProviderType(model.provider_type),
            source_type=ProviderSourceType(model.source_type),
            status=ProviderStatus(model.status),
            display_name=model.display_name,
            description=model.description or "",
            base_url=model.base_url or "",
            api_version=model.api_version or "v1",
            auth_config=json.loads(model.auth_config) if model.auth_config else {},
            operational_config=json.loads(model.operational_config) if model.operational_config else {},
            rate_limit_per_minute=model.rate_limit_per_minute or 60,
            timeout_seconds=model.timeout_seconds or 30,
            created_at=model.created_at,
            updated_at=model.updated_at,
            disabled_at=model.disabled_at,
        )
