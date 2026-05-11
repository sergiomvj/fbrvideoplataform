from __future__ import annotations

from fastapi import APIRouter, Depends
from uuid import UUID

from application.errors import AppError
from application.security.auth import CurrentUser
from api.schemas.review import ReviewQueueItemResponse, ReviewListResponse
from domain.human_review.models import ReviewQueueItem
from infrastructure.db.session import async_session
from infrastructure.db.review_repository import ReviewRepository
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/review", tags=["review"])


async def _get_repo(session: AsyncSession = Depends(async_session)) -> ReviewRepository:
    return ReviewRepository(session)


def _item_to_response(item: ReviewQueueItem) -> ReviewQueueItemResponse:
    scene_label = item.scene_label or f"Scene {item.scene_index}"

    return ReviewQueueItemResponse(
        id=str(item.id),
        production_id=str(item.production_id),
        scene_id=str(item.scene_id),
        scene_index=item.scene_index,
        scene_label=scene_label,
        asset_id=str(getattr(item, "asset_id", getattr(item, "candidate_id", item.id))),
        asset_url=item.asset_url,
        asset_type=item.asset_type,
        source=item.source,
        score=item.score,
        justification=item.rationale,
        decision=item.status,
        status=item.status,
        preview_url=item.preview_url,
    )


@router.get("/{production_id}", response_model=ReviewListResponse)
async def list_pending_reviews(
    production_id: str,
    user: CurrentUser,
    repo: ReviewRepository = Depends(_get_repo),
) -> ReviewListResponse:
    items = await repo.get_pending(UUID(production_id))
    responses = [_item_to_response(item) for item in items]
    return ReviewListResponse(items=responses, total_count=len(responses))


@router.post("/{production_id}/{item_id}/approve", response_model=ReviewQueueItemResponse)
async def approve_review_item(
    production_id: str,
    item_id: str,
    user: CurrentUser,
    repo: ReviewRepository = Depends(_get_repo),
) -> ReviewQueueItemResponse:
    item = await repo.update_status(UUID(item_id), "approved", reviewed_by=user.user_id)
    if not item:
        raise AppError(message="Review item not found", status_code=404)
    return _item_to_response(item)


@router.post("/{production_id}/{item_id}/reject", response_model=ReviewQueueItemResponse)
async def reject_review_item(
    production_id: str,
    item_id: str,
    user: CurrentUser,
    repo: ReviewRepository = Depends(_get_repo),
) -> ReviewQueueItemResponse:
    item = await repo.update_status(UUID(item_id), "rejected", reviewed_by=user.user_id)
    if not item:
        raise AppError(message="Review item not found", status_code=404)
    return _item_to_response(item)


@router.post("/{production_id}/{item_id}/requery", response_model=ReviewQueueItemResponse)
async def requery_review_item(
    production_id: str,
    item_id: str,
    user: CurrentUser,
    repo: ReviewRepository = Depends(_get_repo),
) -> ReviewQueueItemResponse:
    item = await repo.update_status(UUID(item_id), "requeried", reviewed_by=user.user_id)
    if not item:
        raise AppError(message="Review item not found", status_code=404)
    return _item_to_response(item)
