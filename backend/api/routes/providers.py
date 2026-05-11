from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional

from application.errors import AppError
from application.security.auth import CurrentUser
from application.services.provider_registry.service import provider_registry_service
from domain.media_sourcing.provider import (
    ProviderType,
    ProviderSourceType,
    ProviderStatus,
)
from infrastructure.db.session import async_session
from infrastructure.db.provider_repository import ProviderRepository
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/providers", tags=["providers"])


class CreateProviderRequest(BaseModel):
    provider_key: str = Field(min_length=1, max_length=50)
    provider_type: str = Field(default="stock_image")
    source_type: str = Field(default="stock_automatic")
    display_name: str = Field(min_length=1, max_length=100)
    description: str = ""
    base_url: str = ""
    auth_config: dict = Field(default_factory=dict)
    operational_config: dict = Field(default_factory=dict)


class UpdateProviderRequest(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    base_url: Optional[str] = None
    auth_config: Optional[dict] = None
    operational_config: Optional[dict] = None
    rate_limit_per_minute: Optional[int] = None
    timeout_seconds: Optional[int] = None


class ProviderResponse(BaseModel):
    id: str
    provider_key: str
    provider_type: str
    source_type: str
    status: str
    display_name: str
    description: str
    base_url: str
    api_version: str
    rate_limit_per_minute: int
    timeout_seconds: int
    created_at: str
    updated_at: str
    disabled_at: Optional[str] = None


def _to_response(p) -> ProviderResponse:
    return ProviderResponse(
        id=p.id.hex,
        provider_key=p.provider_key,
        provider_type=p.provider_type.value,
        source_type=p.source_type.value,
        status=p.status.value,
        display_name=p.display_name,
        description=p.description,
        base_url=p.base_url,
        api_version=p.api_version,
        rate_limit_per_minute=p.rate_limit_per_minute,
        timeout_seconds=p.timeout_seconds,
        created_at=p.created_at.isoformat(),
        updated_at=p.updated_at.isoformat(),
        disabled_at=p.disabled_at.isoformat() if p.disabled_at else None,
    )


@router.get("/", response_model=list[ProviderResponse])
async def list_providers(
    user: CurrentUser,
    provider_type: Optional[str] = None,
    source_type: Optional[str] = None,
    status: Optional[str] = None,
) -> list[ProviderResponse]:
    pt = ProviderType(provider_type) if provider_type else None
    st = ProviderSourceType(source_type) if source_type else None
    ps = ProviderStatus(status) if status else None
    providers = await provider_registry_service.list_providers(
        provider_type=pt, source_type=st, status=ps
    )
    return [_to_response(p) for p in providers]


@router.get("/{provider_id}", response_model=ProviderResponse)
async def get_provider(
    provider_id: str,
    user: CurrentUser,
) -> ProviderResponse:
    provider = await provider_registry_service.get_provider(UUID(provider_id))
    if not provider:
        raise AppError(message="Provider not found", status_code=404)
    return _to_response(provider)


@router.post("/", response_model=ProviderResponse, status_code=201)
async def create_provider(
    request: CreateProviderRequest,
    user: CurrentUser,
) -> ProviderResponse:
    try:
        pt = ProviderType(request.provider_type)
        st = ProviderSourceType(request.source_type)
    except ValueError as e:
        raise AppError(message=f"Invalid enum value: {e}", status_code=400)

    existing = await provider_registry_service.get_provider_by_key(request.provider_key)
    if existing:
        raise AppError(
            message=f"Provider with key '{request.provider_key}' already exists",
            status_code=409,
        )

    provider = await provider_registry_service.create_provider(
        provider_key=request.provider_key,
        provider_type=pt,
        source_type=st,
        display_name=request.display_name,
        description=request.description,
        base_url=request.base_url,
        auth_config=request.auth_config,
        operational_config=request.operational_config,
    )
    return _to_response(provider)


@router.patch("/{provider_id}", response_model=ProviderResponse)
async def update_provider(
    provider_id: str,
    request: UpdateProviderRequest,
    user: CurrentUser,
) -> ProviderResponse:
    kwargs = {k: v for k, v in request.model_dump().items() if v is not None}
    if not kwargs:
        raise AppError(message="No fields to update", status_code=400)

    provider = await provider_registry_service.update_provider(UUID(provider_id), **kwargs)
    if not provider:
        raise AppError(message="Provider not found", status_code=404)
    return _to_response(provider)


@router.post("/{provider_id}/enable", response_model=ProviderResponse)
async def enable_provider(
    provider_id: str,
    user: CurrentUser,
) -> ProviderResponse:
    provider = await provider_registry_service.enable_provider(UUID(provider_id))
    if not provider:
        raise AppError(message="Provider not found", status_code=404)
    return _to_response(provider)


@router.post("/{provider_id}/disable", response_model=ProviderResponse)
async def disable_provider(
    provider_id: str,
    user: CurrentUser,
) -> ProviderResponse:
    provider = await provider_registry_service.disable_provider(UUID(provider_id))
    if not provider:
        raise AppError(message="Provider not found", status_code=404)
    return _to_response(provider)


@router.delete("/{provider_id}", status_code=200)
async def delete_provider(
    provider_id: str,
    user: CurrentUser,
) -> dict:
    deleted = await provider_registry_service.delete_provider(UUID(provider_id))
    if not deleted:
        raise AppError(message="Provider not found", status_code=404)
    return {"deleted": provider_id}
