from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from uuid import UUID
from typing import Optional

from application.errors import AppError
from application.security.auth import CurrentUser
from application.services.render.submission import render_submission_service
from domain.composition.models import CompositionTimeline
from domain.render.models import RenderJob, RenderJobStatus
from domain.render.submission import SubmissionPayload
from infrastructure.db.session import async_session
from infrastructure.db.composition_repository import CompositionRepository
from infrastructure.db.render_repository import RenderRepository
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/renders", tags=["renders"])


async def _get_session() -> AsyncSession:
    async for s in async_session():
        yield s


class RenderSubmitRequest(BaseModel):
    provider: str = "heygen"
    output_settings: dict = {}
    callback_url: Optional[str] = None


@router.post("/{production_id}/submit")
async def submit_render(
    production_id: str,
    request: RenderSubmitRequest,
    user: CurrentUser,
    session: AsyncSession = Depends(_get_session),
) -> dict:
    comp_repo = CompositionRepository(session)
    render_repo = RenderRepository(session)

    composition = await comp_repo.get_by_production(UUID(production_id))
    if not composition:
        raise AppError(message="Composition not found for this production", status_code=404)

    composition_data = {
        "template_type_id": composition.template_type_id,
        "variation_id": composition.variation_id,
        "total_duration_seconds": composition.total_duration_seconds,
        "scenes": [
            {
                "slot_index": idx,
                "slot_type": s.slot_type,
                "duration_seconds": s.duration_seconds,
                "content_reference": s.content_reference,
                "asset_url": s.asset_url,
            }
            for idx, s in enumerate(composition.slots)
        ],
    }

    payload = SubmissionPayload(
        production_id=UUID(production_id),
        composition_data=composition_data,
        output_settings=request.output_settings,
        callback_url=request.callback_url,
    )

    result = await render_submission_service.submit(
        payload=payload,
        provider=request.provider,
    )

    if not result.is_success:
        raise AppError(
            message=f"Render submission failed: {result.error_message or result.outcome.value}",
            status_code=422,
        )

    job = RenderJob(
        production_id=UUID(production_id),
        composition_id=composition.id,
        provider=request.provider,
        external_job_id=result.external_job_id,
        status=RenderJobStatus.QUEUED,
    )
    await render_repo.save_job(job)

    return {
        "job_id": str(job.id),
        "production_id": str(job.production_id),
        "composition_id": str(job.composition_id),
        "provider": job.provider,
        "external_job_id": job.external_job_id,
        "status": job.status.value,
        "created_at": job.created_at.isoformat(),
        "submission_id": result.submission_id.hex,
    }


@router.get("/{production_id}/status")
async def get_render_status(
    production_id: str,
    user: CurrentUser,
    session: AsyncSession = Depends(_get_session),
) -> dict:
    render_repo = RenderRepository(session)
    job = await render_repo.get_by_production(UUID(production_id))
    if not job:
        raise AppError(message="No render job found for this production", status_code=404)
    return {
        "job_id": str(job.id),
        "production_id": str(job.production_id),
        "status": job.status.value,
        "external_job_id": job.external_job_id,
        "provider": job.provider,
        "created_at": job.created_at.isoformat(),
        "updated_at": job.updated_at.isoformat(),
        "error_message": job.error_message,
    }


@router.post("/{production_id}/reconcile")
async def reconcile_render(
    production_id: str,
    user: CurrentUser,
    session: AsyncSession = Depends(_get_session),
) -> dict:
    render_repo = RenderRepository(session)
    job = await render_repo.get_by_production(UUID(production_id))
    if not job:
        raise AppError(message="No render job found for this production", status_code=404)
    if not job.external_job_id:
        raise AppError(message="No external job ID to reconcile", status_code=400)

    submissions = render_submission_service.get_submissions_for_production(UUID(production_id))
    if not submissions:
        raise AppError(message="No submission found for reconciliation", status_code=404)

    submission = submissions[-1]
    job_state = await render_submission_service.reconcile_job_state(
        submission_id=submission.submission_id,
        provider=job.provider,
        external_job_id=job.external_job_id,
    )

    if not job_state:
        raise AppError(message="Failed to reconcile job state", status_code=500)

    new_status = RenderJobStatus.PROCESSING
    if job_state.status == "completed":
        new_status = RenderJobStatus.COMPLETED
    elif job_state.status == "failed":
        new_status = RenderJobStatus.FAILED

    updated = await render_repo.update_status(
        job.id, new_status, error_message=job_state.error
    )

    return {
        "job_id": str(job.id),
        "status": new_status.value,
        "progress": job_state.progress,
        "external_job_id": job.external_job_id,
        "updated_at": updated.updated_at.isoformat() if updated else None,
    }
