from uuid import UUID, uuid4
from typing import Optional
import time

from domain.render import (
    SubmissionPayload,
    SubmissionResult,
    SubmissionOutcome,
    SubmissionStatus,
    FailureType,
    ProviderJobState,
    RenderSubmissionContract,
)
from domain.audit import audit_service, AuditEventType
from infrastructure.logging import get_logger, LoggingContext

logger = get_logger(__name__)


class RenderSubmissionService:
    def __init__(self):
        self._submissions: dict[UUID, RenderSubmissionContract] = {}
        self._repository = None

    def set_repository(self, repository) -> None:
        self._repository = repository

    async def submit(
        self,
        payload: SubmissionPayload,
        provider: str,
    ) -> SubmissionResult:
        start_time = time.time()

        contract = RenderSubmissionContract(
            production_id=payload.production_id,
            provider=provider,
            payload=payload,
            status=SubmissionStatus.VALIDATING,
        )
        self._submissions[contract.submission_id] = contract
        await self._persist(contract)

        with LoggingContext(
            production_id=payload.production_id.hex,
            submission_id=contract.submission_id.hex,
        ):
            validation_errors = await self._validate_payload(payload)
            if validation_errors:
                contract.status = SubmissionStatus.FAILED
                contract.result = SubmissionResult(
                    outcome=SubmissionOutcome.VALIDATION_FAILED,
                    validation_errors=validation_errors,
                    duration_ms=(time.time() - start_time) * 1000,
                )
                logger.warning("validation_failed", errors=validation_errors)
                await self._persist(contract)
                return contract.result

            logger.info("payload_validated", provider=provider)

            submission_result = await self._submit_to_provider(
                payload, provider, contract.submission_id
            )

            contract.status = (
                SubmissionStatus.SUBMITTED
                if submission_result.is_success
                else SubmissionStatus.FAILED
            )
            contract.result = submission_result
            contract.updated_at = submission_result.submitted_at or contract.updated_at
            await self._persist(contract)

            logger.info(
                "submission_completed",
                provider=provider,
                outcome=submission_result.outcome.value,
                external_job_id=submission_result.external_job_id,
            )

            return submission_result

    async def _validate_payload(self, payload: SubmissionPayload) -> list[str]:
        errors = []

        if not payload.production_id:
            errors.append("production_id is required")

        if not payload.composition_data:
            errors.append("composition_data is required")
        elif not payload.composition_data.get("scenes"):
            errors.append("composition_data.scenes is required")

        if not payload.output_settings:
            errors.append("output_settings is required")

        return errors

    async def _submit_to_provider(
        self,
        payload: SubmissionPayload,
        provider: str,
        submission_id: UUID,
    ) -> SubmissionResult:
        try:
            provider_payload = payload.to_provider_format(provider)

            logger.info("submitting_to_provider", provider=provider)

            external_job_id = await self._call_provider_api(provider, provider_payload)

            return SubmissionResult(
                outcome=SubmissionOutcome.SUCCESS,
                external_job_id=external_job_id,
                submitted_at=__import__("datetime").datetime.utcnow(),
                provider_response={"status": "submitted"},
                duration_ms=0.0,
            )

        except TimeoutError:
            return SubmissionResult(
                outcome=SubmissionOutcome.SUBMISSION_FAILED,
                error_message="Provider timeout",
                failure_type=FailureType.TIMEOUT,
            )
        except Exception as e:
            error_str = str(e).lower()
            if "auth" in error_str or "unauthorized" in error_str:
                failure_type = FailureType.AUTH_ERROR
            elif "rate" in error_str:
                failure_type = FailureType.RATE_LIMITED
            else:
                failure_type = FailureType.PROVIDER_SUBMISSION_ERROR

            return SubmissionResult(
                outcome=SubmissionOutcome.SUBMISSION_FAILED,
                error_message=str(e),
                failure_type=failure_type,
            )

    async def _call_provider_api(self, provider: str, payload: dict) -> str:
        return f"{provider}_job_{uuid4().hex[:8]}"

    async def reconcile_job_state(
        self,
        submission_id: UUID,
        provider: str,
        external_job_id: str,
    ) -> Optional[ProviderJobState]:
        contract = await self.get_submission(submission_id)
        if not contract:
            logger.warning("submission_not_found", submission_id=submission_id.hex)
            return None

        self._submissions[contract.submission_id] = contract

        job_state = await self._poll_provider_status(provider, external_job_id)

        contract.job_states.append(job_state)
        await self._persist(contract)

        logger.info(
            "job_state_reconciled",
            submission_id=submission_id.hex,
            provider=provider,
            status=job_state.status,
            progress=job_state.progress,
        )

        return job_state

    async def _poll_provider_status(
        self, provider: str, external_job_id: str
    ) -> ProviderJobState:
        return ProviderJobState(
            external_job_id=external_job_id,
            provider=provider,
            status="processing",
            progress=0.5,
        )

    async def handle_webhook(
        self,
        submission_id: UUID,
        provider: str,
        webhook_payload: dict,
    ) -> Optional[RenderSubmissionContract]:
        contract = await self.get_submission(submission_id)
        if not contract:
            return None

        self._submissions[contract.submission_id] = contract

        status = webhook_payload.get("status", "")

        job_state = ProviderJobState(
            external_job_id=webhook_payload.get("external_job_id", ""),
            provider=provider,
            status=status,
            progress=webhook_payload.get("progress", 1.0),
            result_url=webhook_payload.get("result_url"),
            error=webhook_payload.get("error"),
            webhook_received_at=__import__("datetime").datetime.utcnow(),
        )
        contract.job_states.append(job_state)

        if status in ["completed", "failed"]:
            contract.status = (
                SubmissionStatus.COMPLETED
                if status == "completed"
                else SubmissionStatus.FAILED
            )

            self._emit_completion_audit(contract, status)

        await self._persist(contract)

        logger.info(
            "webhook_received",
            submission_id=submission_id.hex,
            provider=provider,
            status=status,
        )

        return contract

    async def get_submission(self, submission_id: UUID) -> Optional[RenderSubmissionContract]:
        if self._repository:
            try:
                contract = await self._repository.get_by_id(submission_id)
                if contract:
                    self._submissions[contract.submission_id] = contract
                    return contract
            except Exception:
                pass
        contract = self._submissions.get(submission_id)
        if contract:
            return contract
        return None

    async def get_submissions_for_production(
        self, production_id: UUID
    ) -> list[RenderSubmissionContract]:
        if self._repository:
            try:
                results = await self._repository.get_by_production(production_id)
                if results:
                    for contract in results:
                        self._submissions[contract.submission_id] = contract
                    return results
            except Exception:
                pass
        memory_results = [
            s for s in self._submissions.values() if s.production_id == production_id
        ]
        return memory_results if memory_results else []

    async def _persist(self, contract: RenderSubmissionContract) -> None:
        if self._repository:
            try:
                await self._repository.save(contract)
            except Exception as e:
                logger.warning("submission_persist_failed", submission_id=contract.submission_id.hex, error=str(e))

    def _emit_completion_audit(self, contract: RenderSubmissionContract, status: str) -> None:
        if status == "completed":
            event_type = AuditEventType.RENDER_JOB_COMPLETED
        else:
            event_type = AuditEventType.RENDER_JOB_FAILED

        audit_service.emit(
            event_type=event_type,
            entity_type="render_submission",
            entity_id=contract.submission_id.hex,
            metadata={
                "production_id": contract.production_id.hex,
                "provider": contract.provider,
                "external_job_id": contract.result.external_job_id if contract.result else None,
            },
        )


render_submission_service = RenderSubmissionService()