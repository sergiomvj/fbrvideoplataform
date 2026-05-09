from uuid import UUID
from typing import Optional

from domain.visual_planning.models import VisualBrief
from domain.media_sourcing import MediaCandidate, SourcingResult
from domain.context_verification import (
    VerificationResult,
    OperationalDecision,
    context_scorer,
)
from domain.audit import audit_service, AuditEventType
from infrastructure.logging import get_logger, LoggingContext
from infrastructure.metrics import metrics_collector

logger = get_logger(__name__)


class ContextVerificationService:
    async def verify_candidates(
        self,
        candidates: list[MediaCandidate],
        briefs: list[VisualBrief],
        production_id: UUID,
    ) -> list[VerificationResult]:
        results = []

        with LoggingContext(production_id=production_id.hex):
            for candidate in candidates:
                brief = self._find_matching_brief(candidate, briefs)
                if not brief:
                    logger.warning("no_brief_matching_candidate", candidate_id=candidate.id.hex)
                    continue

                result = await self.verify_single(candidate, brief, production_id)
                results.append(result)

        return results

    async def verify_single(
        self,
        candidate: MediaCandidate,
        brief: VisualBrief,
        production_id: UUID,
    ) -> VerificationResult:
        with LoggingContext(
            production_id=production_id.hex,
            scene_id=brief.scene_id.hex,
            asset_id=candidate.id.hex,
        ):
            logger.info("verification_started", candidate_id=candidate.id.hex)

            result = context_scorer.score(candidate, brief, production_id)

            self._emit_audit_event(result)
            self._record_metrics(result)

            logger.info(
                "verification_completed",
                candidate_id=candidate.id.hex,
                score=result.score,
                decision=result.decision.value,
            )

            return result

    async def verify_sourcing_result(
        self,
        sourcing_result: SourcingResult,
        brief: VisualBrief,
        production_id: UUID,
    ) -> list[VerificationResult]:
        results = []

        if not sourcing_result.is_success:
            logger.warning(
                "sourcing_failed_skipping_verification",
                provider=sourcing_result.provider,
                outcome=sourcing_result.outcome.value,
            )
            return results

        for candidate in sourcing_result.candidates:
            result = await self.verify_single(candidate, brief, production_id)
            results.append(result)

        return results

    def _find_matching_brief(
        self, candidate: MediaCandidate, briefs: list[VisualBrief]
    ) -> Optional[VisualBrief]:
        for brief in briefs:
            if hasattr(brief, "scene_id"):
                return brief
        return briefs[0] if briefs else None

    def _emit_audit_event(self, result: VerificationResult) -> None:
        if result.is_auto_approved:
            event_type = AuditEventType.DECISION_AUTO_APPROVED
        elif result.requires_review:
            event_type = AuditEventType.DECISION_MANUAL_REVIEW
        else:
            event_type = AuditEventType.CONTEXT_VERIFICATION_FAILED

        audit_service.emit(
            event_type=event_type,
            entity_type="verification_result",
            entity_id=result.id.hex,
            before_state=None,
            after_state={
                "score": result.score,
                "decision": result.decision.value,
                "flags": [f.value for f in result.flags],
            },
            metadata={
                "candidate_id": result.candidate_id.hex,
                "brief_id": result.brief_id.hex,
                "rationale": result.rationale,
            },
        )

    def _record_metrics(self, result: VerificationResult) -> None:
        metrics_collector.record_decision(
            decision_type="context_verification",
            outcome=result.decision.value,
        )

        metrics_collector.record_context_verification(
            check_type="overall",
            score=result.score / 100.0,
        )


context_verification_service = ContextVerificationService()