from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4


class RenderJobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class RenderJob:
    id: UUID = field(default_factory=uuid4)
    production_id: UUID = field(default_factory=uuid4)
    composition_id: UUID = field(default_factory=uuid4)
    provider: str = ""
    external_job_id: str | None = None
    status: RenderJobStatus = RenderJobStatus.QUEUED
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    error_message: str | None = None


class RenderJobStore:
    def __init__(self) -> None:
        self._jobs: dict[UUID, RenderJob] = {}

    async def add(self, job: RenderJob) -> RenderJob:
        self._jobs[job.id] = job
        return job

    async def get(self, job_id: UUID) -> RenderJob | None:
        return self._jobs.get(job_id)

    async def get_by_production(self, production_id: UUID) -> RenderJob | None:
        for job in self._jobs.values():
            if job.production_id == production_id:
                return job
        return None

    async def update_status(
        self,
        job_id: UUID,
        status: RenderJobStatus,
        error_message: str | None = None,
    ) -> RenderJob | None:
        job = self._jobs.get(job_id)
        if job:
            job.status = status
            job.updated_at = datetime.now(timezone.utc)
            if error_message is not None:
                job.error_message = error_message
        return job


render_job_store = RenderJobStore()
