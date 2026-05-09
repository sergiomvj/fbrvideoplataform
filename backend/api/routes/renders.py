from __future__ import annotations

from fastapi import APIRouter
from uuid import UUID

from application.errors import AppError
from application.security.auth import CurrentUser
from domain.composition.models import CompositionTimeline
from domain.render.models import RenderJobStatus, render_job_store
from integrations.heygen.adapter import HeyGenAdapter

router = APIRouter(prefix="/renders", tags=["renders"])

_composition_store: dict[str, CompositionTimeline] = {}
_adapter = HeyGenAdapter()


@router.post("/{production_id}/submit")
async def submit_render(
    production_id: str,
    user: CurrentUser,
) -> dict:
    composition = _composition_store.get(production_id)
    if not composition:
        raise AppError(message="Composition not found for this production", status_code=404)

    job = await _adapter.submit_render_job(composition, production_id)
    return {
        "job_id": str(job.id),
        "production_id": str(job.production_id),
        "composition_id": str(job.composition_id),
        "provider": job.provider,
        "status": job.status.value,
        "created_at": job.created_at.isoformat(),
    }


@router.get("/{production_id}/status")
async def get_render_status(
    production_id: str,
    user: CurrentUser,
) -> dict:
    job = await render_job_store.get_by_production(UUID(production_id))
    if not job:
        raise AppError(message="No render job found for this production", status_code=404)
    return {
        "job_id": str(job.id),
        "production_id": str(job.production_id),
        "status": job.status.value,
        "external_job_id": job.external_job_id,
        "created_at": job.created_at.isoformat(),
        "updated_at": job.updated_at.isoformat(),
        "error_message": job.error_message,
    }


def register_composition(production_id: str, composition: CompositionTimeline) -> None:
    _composition_store[production_id] = composition
