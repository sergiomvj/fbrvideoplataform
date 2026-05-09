from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.render.submission import (
    RenderSubmissionContract,
    SubmissionStatus,
    SubmissionOutcome,
    SubmissionResult,
    SubmissionPayload,
    ProviderJobState,
    FailureType,
)
from infrastructure.db.models import RenderSubmissionModel


class RenderSubmissionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, contract: RenderSubmissionContract) -> RenderSubmissionContract:
        existing = await self._get_model(contract.submission_id)
        if existing:
            existing.status = contract.status.value
            existing.outcome = contract.result.outcome.value if contract.result else None
            existing.external_job_id = contract.result.external_job_id if contract.result else None
            existing.error_message = contract.result.error_message if contract.result else None
            existing.failure_type = contract.result.failure_type.value if contract.result and contract.result.failure_type else None
            existing.provider_response_json = json.dumps(contract.result.provider_response) if contract.result else "{}"
            existing.job_states_json = json.dumps([
                {
                    "external_job_id": js.external_job_id,
                    "provider": js.provider,
                    "status": js.status,
                    "progress": js.progress,
                    "message": js.message,
                    "result_url": js.result_url,
                    "error": js.error,
                }
                for js in contract.job_states
            ])
            existing.updated_at = datetime.now(timezone.utc)
        else:
            model = RenderSubmissionModel(
                id=str(contract.submission_id),
                production_id=str(contract.production_id),
                provider=contract.provider,
                status=contract.status.value,
                outcome=contract.result.outcome.value if contract.result else None,
                external_job_id=contract.result.external_job_id if contract.result else None,
                error_message=contract.result.error_message if contract.result else None,
                failure_type=contract.result.failure_type.value if contract.result and contract.result.failure_type else None,
                payload_json=json.dumps({
                    "production_id": contract.payload.production_id.hex,
                    "composition_data": contract.payload.composition_data,
                    "output_settings": contract.payload.output_settings,
                    "callback_url": contract.payload.callback_url,
                    "idempotency_key": contract.payload.idempotency_key,
                }),
                provider_response_json=json.dumps(contract.result.provider_response) if contract.result else "{}",
                job_states_json="[]",
                created_at=contract.created_at,
                updated_at=contract.updated_at,
            )
            self.session.add(model)

        await self.session.flush()
        return contract

    async def get_by_id(self, submission_id: UUID) -> Optional[RenderSubmissionContract]:
        model = await self._get_model(submission_id)
        if model is None:
            return None
        return self._to_domain(model)

    async def get_by_production(self, production_id: UUID) -> list[RenderSubmissionContract]:
        stmt = (
            select(RenderSubmissionModel)
            .where(RenderSubmissionModel.production_id == str(production_id))
            .order_by(RenderSubmissionModel.created_at)
        )
        result = await self.session.execute(stmt)
        return [self._to_domain(m) for m in result.scalars().all()]

    async def _get_model(self, submission_id: UUID) -> Optional[RenderSubmissionModel]:
        stmt = select(RenderSubmissionModel).where(
            RenderSubmissionModel.id == str(submission_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    def _to_domain(self, model: RenderSubmissionModel) -> RenderSubmissionContract:
        payload_data = json.loads(model.payload_json) if model.payload_json else {}
        payload = SubmissionPayload(
            production_id=UUID(payload_data.get("production_id", model.production_id)),
            composition_data=payload_data.get("composition_data", {}),
            output_settings=payload_data.get("output_settings", {}),
            callback_url=payload_data.get("callback_url"),
            idempotency_key=payload_data.get("idempotency_key", ""),
        )

        result = None
        if model.outcome:
            result = SubmissionResult(
                outcome=SubmissionOutcome(model.outcome),
                external_job_id=model.external_job_id,
                error_message=model.error_message,
                failure_type=FailureType(model.failure_type) if model.failure_type else None,
                provider_response=json.loads(model.provider_response_json) if model.provider_response_json else {},
            )

        job_states = []
        if model.job_states_json:
            try:
                states_data = json.loads(model.job_states_json)
                for js in states_data:
                    job_states.append(ProviderJobState(
                        external_job_id=js.get("external_job_id", ""),
                        provider=js.get("provider", ""),
                        status=js.get("status", ""),
                        progress=js.get("progress", 0.0),
                        message=js.get("message"),
                        result_url=js.get("result_url"),
                        error=js.get("error"),
                    ))
            except (json.JSONDecodeError, KeyError):
                pass

        return RenderSubmissionContract(
            submission_id=UUID(model.id),
            production_id=UUID(model.production_id),
            provider=model.provider,
            payload=payload,
            status=SubmissionStatus(model.status),
            result=result,
            job_states=job_states,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
