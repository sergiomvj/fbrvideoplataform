from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.render.models import RenderJob, RenderJobStatus
from infrastructure.db.models import RenderJobModel, RenderJobEventModel


class RenderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save_job(self, job: RenderJob) -> RenderJob:
        model = RenderJobModel(
            id=str(job.id),
            production_id=str(job.production_id),
            composition_id=str(job.composition_id) if job.composition_id else None,
            provider=job.provider,
            external_job_id=job.external_job_id,
            status=job.status.value,
            error_message=job.error_message,
            created_at=job.created_at,
            updated_at=job.updated_at,
        )
        self.session.add(model)
        await self.session.flush()
        return job

    async def get_by_production(self, production_id: UUID) -> RenderJob | None:
        stmt = select(RenderJobModel).where(
            RenderJobModel.production_id == str(production_id)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def get_by_id(self, job_id: UUID) -> RenderJob | None:
        stmt = select(RenderJobModel).where(
            RenderJobModel.id == str(job_id)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def update_status(
        self,
        job_id: UUID,
        status: RenderJobStatus,
        error_message: str | None = None,
    ) -> RenderJob | None:
        stmt = select(RenderJobModel).where(
            RenderJobModel.id == str(job_id)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        old_status = model.status
        model.status = status.value
        model.updated_at = datetime.now(timezone.utc)
        if error_message is not None:
            model.error_message = error_message
        event = RenderJobEventModel(
            render_job_id=str(job_id),
            from_status=old_status,
            to_status=status.value,
        )
        self.session.add(event)
        await self.session.flush()
        return self._to_domain(model)

    def _to_domain(self, model: RenderJobModel) -> RenderJob:
        job = RenderJob.__new__(RenderJob)
        job.id = UUID(model.id)
        job.production_id = UUID(model.production_id)
        job.composition_id = UUID(model.composition_id) if model.composition_id else job.production_id
        job.provider = model.provider
        job.external_job_id = model.external_job_id
        job.status = RenderJobStatus(model.status)
        job.created_at = model.created_at
        job.updated_at = model.updated_at
        job.error_message = model.error_message
        return job
