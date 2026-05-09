from __future__ import annotations

from fastapi import APIRouter
from uuid import UUID

from application.errors import AppError
from application.security.auth import CurrentUser
from domain.human_review.models import review_queue

router = APIRouter(prefix="/review", tags=["review"])


@router.get("/{production_id}")
async def list_pending_reviews(
    production_id: str,
    user: CurrentUser,
) -> dict:
    items = await review_queue.get_pending(UUID(production_id))
    return {
        "production_id": production_id,
        "items": [
            {
                "id": str(i.id),
                "scene_id": str(i.scene_id),
                "asset_id": str(i.asset_id),
                "status": i.status,
            }
            for i in items
        ],
    }


@router.post("/{production_id}/{item_id}/approve")
async def approve_review_item(
    production_id: str,
    item_id: str,
    user: CurrentUser,
) -> dict:
    item = await review_queue.approve(UUID(item_id))
    if not item:
        raise AppError(message="Review item not found", status_code=404)
    return {
        "id": str(item.id),
        "production_id": str(item.production_id),
        "status": item.status,
    }


@router.post("/{production_id}/{item_id}/reject")
async def reject_review_item(
    production_id: str,
    item_id: str,
    user: CurrentUser,
) -> dict:
    item = await review_queue.reject(UUID(item_id))
    if not item:
        raise AppError(message="Review item not found", status_code=404)
    return {
        "id": str(item.id),
        "production_id": str(item.production_id),
        "status": item.status,
    }
