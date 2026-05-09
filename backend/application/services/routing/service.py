from uuid import UUID
from typing import Optional
from datetime import datetime

from domain.context_verification import VerificationResult, OperationalDecision
from domain.human_review import (
    RequeryWorkflow,
    requery_workflow,
    RequeryAttempt,
    ReviewQueueItem,
    ReviewQueueStatus,
)
from domain.audit import audit_service, AuditEventType
from infrastructure.logging import get_logger, LoggingContext

logger = get_logger(__name__)


class RoutingService:
    MIN_REVIEW_SCORE_THRESHOLD = 60.0

    def __init__(self):
        self._requery_workflow = requery_workflow
        self._review_queue: dict[UUID, ReviewQueueItem] = {}
        self._query_builder = None
        self._review_repository = None

    def set_query_builder(self, query_builder) -> None:
        self._query_builder = query_builder

    def set_review_repository(self, repository) -> None:
        self._review_repository = repository

    async def route_verification_result(
        self,
        result: VerificationResult,
        brief_data: dict,
        candidate_data: dict,
    ) -> str:
        with LoggingContext(
            production_id=result.production_id.hex,
            scene_id=result.brief_id.hex,
            asset_id=result.candidate_id.hex,
        ):
            decision = result.decision

            if result.score < self.MIN_REVIEW_SCORE_THRESHOLD:
                logger.info(
                    "score_below_threshold",
                    score=result.score,
                    threshold=self.MIN_REVIEW_SCORE_THRESHOLD,
                    candidate_id=result.candidate_id.hex,
                )
                return self._handle_requery(result)

            if decision == OperationalDecision.REQUERY_NEEDED:
                return self._handle_requery(result)
            elif decision == OperationalDecision.REVIEW_REQUIRED:
                return await self._handle_review_queue(result, brief_data, candidate_data)
            elif decision == OperationalDecision.AUTO_APPROVED:
                logger.info("auto_approved_skipping_queue", score=result.score)
                return "auto_approved"

            return "unknown"

    def _handle_requery(self, result: VerificationResult) -> str:
        existing = self._find_existing_requery_attempt(
            result.production_id, result.candidate_id
        )

        if existing:
            if existing.can_retry():
                self._requery_workflow.record_retry(existing.id)
                logger.info(
                    "requery_retry_attempt",
                    attempt_number=existing.attempt_number,
                    candidate_id=result.candidate_id.hex,
                )
                self._emit_requery_audit(result, existing.attempt_number)
                return "requery_retry"
            else:
                self._requery_workflow.mark_failure(
                    existing.id, "Max retry attempts exhausted"
                )
                logger.warning(
                    "structural_failure",
                    candidate_id=result.candidate_id.hex,
                    attempts=existing.attempt_number,
                )
                self._emit_structural_failure_audit(result, existing.attempt_number)
                return "structural_failure"
        else:
            attempt = self._requery_workflow.create_attempt(
                production_id=result.production_id,
                scene_id=result.brief_id,
                candidate_id=result.candidate_id,
            )
            logger.info(
                "requery_created",
                attempt_id=attempt.id.hex,
                candidate_id=result.candidate_id.hex,
            )
            self._emit_requery_audit(result, 1)
            return "requery_created"

    async def _handle_review_queue(
        self,
        result: VerificationResult,
        brief_data: dict,
        candidate_data: dict,
    ) -> str:
        item = ReviewQueueItem(
            production_id=result.production_id,
            scene_id=result.brief_id,
            candidate_id=result.candidate_id,
            brief_data=brief_data,
            candidate_data=candidate_data,
            score=result.score,
            rationale=result.rationale,
            flags=[f.value for f in result.flags],
        )

        self._review_queue[item.id] = item

        if self._review_repository:
            try:
                await self._review_repository.save_item(item)
            except Exception as e:
                logger.warning("review_item_persist_failed", item_id=item.id.hex, error=str(e))

        logger.info(
            "review_queue_item_created",
            item_id=item.id.hex,
            candidate_id=result.candidate_id.hex,
            score=result.score,
        )

        self._emit_review_audit(result, item.id.hex)

        return "review_queue"

    def _find_existing_requery_attempt(
        self, production_id: UUID, candidate_id: UUID
    ) -> Optional[RequeryAttempt]:
        for attempt in self._requery_workflow.get_active_attempts(production_id):
            if attempt.candidate_id == candidate_id:
                return attempt
        return None

    def get_review_queue(self, production_id: UUID) -> list[ReviewQueueItem]:
        return [
            item
            for item in self._review_queue.values()
            if item.production_id == production_id
            and item.status == ReviewQueueStatus.PENDING
        ]

    def approve_review_item(
        self, item_id: UUID, reviewer: str
    ) -> ReviewQueueItem | None:
        item = self._review_queue.get(item_id)
        if item:
            item.status = ReviewQueueStatus.APPROVED
            item.reviewed_at = datetime.utcnow()
            item.reviewed_by = reviewer
            logger.info("review_item_approved", item_id=item_id.hex, reviewer=reviewer)
            return item
        return None

    def reject_review_item(
        self, item_id: UUID, reviewer: str
    ) -> ReviewQueueItem | None:
        item = self._review_queue.get(item_id)
        if item:
            item.status = ReviewQueueStatus.REJECTED
            item.reviewed_at = datetime.utcnow()
            item.reviewed_by = reviewer
            logger.info("review_item_rejected", item_id=item_id.hex, reviewer=reviewer)
            return item
        return None

    def _emit_requery_audit(self, result: VerificationResult, attempt: int) -> None:
        audit_service.emit(
            event_type=AuditEventType.CONTEXT_VERIFICATION_FAILED,
            entity_type="requery_attempt",
            entity_id=result.candidate_id.hex,
            metadata={
                "score": result.score,
                "attempt": attempt,
                "production_id": result.production_id.hex,
            },
        )

    def _emit_structural_failure_audit(
        self, result: VerificationResult, attempts: int
    ) -> None:
        audit_service.emit(
            event_type=AuditEventType.DECISION_REJECTED,
            entity_type="structural_failure",
            entity_id=result.candidate_id.hex,
            metadata={
                "score": result.score,
                "attempts": attempts,
                "reason": "Max retry attempts exhausted",
                "production_id": result.production_id.hex,
            },
        )

    def _emit_review_audit(
        self, result: VerificationResult, item_id: str
    ) -> None:
        audit_service.emit(
            event_type=AuditEventType.DECISION_MANUAL_REVIEW,
            entity_type="review_queue_item",
            entity_id=item_id,
            metadata={
                "score": result.score,
                "rationale": result.rationale,
                "flags": [f.value for f in result.flags],
                "production_id": result.production_id.hex,
            },
        )


routing_service = RoutingService()