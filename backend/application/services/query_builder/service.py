from uuid import UUID
from typing import Optional

from domain.visual_planning import VisualBrief, VisualFunction
from domain.media_sourcing import (
    QueryStrategy,
    QueryStrategyType,
    QueryAttempt,
    DiagnosticCategory,
    QueryReformulation,
)
from infrastructure.logging import get_logger, LoggingContext

logger = get_logger(__name__)


class QueryBuilderService:
    MIN_REVIEW_THRESHOLD = 60.0

    def __init__(self):
        self._attempts: dict[UUID, QueryAttempt] = {}

    def build_strategy_from_brief(self, brief: VisualBrief) -> QueryStrategy:
        keywords = []
        exclusions = list(brief.proibidos) if brief.proibidos else []

        if brief.tema:
            keywords.append(brief.tema)

        if brief.assunto_visivel:
            keywords.append(brief.assunto_visivel)

        if brief.contexto_geografico_cultural:
            keywords.append(brief.contexto_geografico_cultural)

        for term in brief.permitidos[:3]:
            if term not in keywords:
                keywords.append(term)

        strategy_type = self._determine_strategy_type(brief.funcao_visual)

        orientation = self._map_orientation(brief.funcao_visual.value)

        return QueryStrategy(
            strategy_type=strategy_type,
            keywords=keywords,
            exclusions=exclusions[:5],
            aspect_ratio="16:9",
            orientation=orientation,
            media_type=brief.tipo_ativo_preferido.value,
        )

    def _determine_strategy_type(self, funcao_visual: VisualFunction) -> QueryStrategyType:
        if funcao_visual == VisualFunction.EVIDENCIA_LITERAL:
            return QueryStrategyType.LITERAL
        elif funcao_visual == VisualFunction.CONTEXTO_AMBIENTAL:
            return QueryStrategyType.CONTEXTUAL
        elif funcao_visual == VisualFunction.COBERTURA_BROLL:
            return QueryStrategyType.BROAD
        return QueryStrategyType.CONTEXTUAL

    def _map_orientation(self, funcao: str) -> str:
        if funcao in ["evidencia_literal", "prova_documental"]:
            return "landscape"
        elif funcao == "metafora_controlada":
            return "square"
        return "landscape"

    def create_attempt(
        self,
        production_id: UUID,
        scene_id: UUID,
        brief_id: UUID,
        strategy: QueryStrategy,
        provider_key: str,
        query_params: dict,
    ) -> QueryAttempt:
        existing_attempts = self._get_attempts_for_scene(production_id, scene_id)
        attempt_number = len(existing_attempts) + 1

        attempt = QueryAttempt(
            production_id=production_id,
            scene_id=scene_id,
            brief_id=brief_id,
            strategy=strategy,
            provider_key=provider_key,
            attempt_number=attempt_number,
            query_params=query_params,
        )

        self._attempts[attempt.id] = attempt

        logger.info(
            "query_attempt_created",
            attempt_id=attempt.id.hex,
            production_id=production_id.hex,
            scene_id=scene_id.hex,
            strategy_type=strategy.strategy_type.value,
            attempt_number=attempt_number,
        )

        return attempt

    def record_attempt_result(
        self,
        attempt_id: UUID,
        candidate_count: int,
        diagnostic: Optional[DiagnosticCategory] = None,
        diagnostic_details: str = "",
    ) -> QueryAttempt | None:
        attempt = self._attempts.get(attempt_id)
        if not attempt:
            return None

        attempt.candidate_count = candidate_count
        attempt.diagnostic = diagnostic
        attempt.diagnostic_details = diagnostic_details

        import datetime

        attempt.completed_at = datetime.datetime.utcnow()

        logger.info(
            "query_attempt_completed",
            attempt_id=attempt_id.hex,
            candidate_count=candidate_count,
            diagnostic=diagnostic.value if diagnostic else None,
        )

        return attempt

    def should_requery(self, attempt: QueryAttempt) -> bool:
        return (
            attempt.candidate_count == 0
            or attempt.diagnostic in [
                DiagnosticCategory.THEME_MISMATCH,
                DiagnosticCategory.SCENE_MISMATCH,
                DiagnosticCategory.QUALITY_TOO_LOW,
                DiagnosticCategory.NO_RELEVANT_RESULTS,
            ]
        )

    def should_escalate_to_review(self, attempt: QueryAttempt) -> bool:
        return (
            attempt.candidate_count > 0
            and not self.should_requery(attempt)
            and attempt.attempt_number >= 2
        )

    def create_reformulation(
        self,
        attempt: QueryAttempt,
        reason: str,
    ) -> QueryReformulation:
        reformulated_strategy = self._reformulate_strategy(attempt.strategy, attempt.diagnostic)

        logger.info(
            "query_reformulated",
            original_attempt_id=attempt.id.hex,
            reformulated_strategy_type=reformulated_strategy.strategy_type.value,
            reason=reason,
        )

        return QueryReformulation(
            original_attempt=attempt,
            reformulated_strategy=reformulated_strategy,
            reformulation_reason=reason,
        )

    def _reformulate_strategy(
        self, original: QueryStrategy, diagnostic: Optional[DiagnosticCategory]
    ) -> QueryStrategy:
        if diagnostic == DiagnosticCategory.THEME_MISMATCH:
            return QueryStrategy(
                strategy_type=QueryStrategyType.BROAD,
                keywords=original.keywords[:2],
                exclusions=original.exclusions,
                aspect_ratio=original.aspect_ratio,
                orientation=original.orientation,
                media_type=original.media_type,
                max_results=original.max_results + 5,
            )
        elif diagnostic == DiagnosticCategory.SCENE_MISMATCH:
            return QueryStrategy(
                strategy_type=QueryStrategyType.LITERAL,
                keywords=[original.keywords[0]] if original.keywords else [],
                exclusions=original.exclusions,
                aspect_ratio=original.aspect_ratio,
                orientation=original.orientation,
                media_type=original.media_type,
                max_results=original.max_results,
            )

        return QueryStrategy(
            strategy_type=QueryStrategyType.FALLBACK,
            keywords=original.keywords[:3],
            exclusions=[],
            aspect_ratio="any",
            orientation="any",
            media_type="any",
            max_results=original.max_results + 10,
        )

    def _get_attempts_for_scene(
        self, production_id: UUID, scene_id: UUID
    ) -> list[QueryAttempt]:
        return [
            a
            for a in self._attempts.values()
            if a.production_id == production_id and a.scene_id == scene_id
        ]

    def get_attempts_for_production(
        self, production_id: UUID
    ) -> list[QueryAttempt]:
        return [a for a in self._attempts.values() if a.production_id == production_id]

    def get_latest_attempt(
        self, production_id: UUID, scene_id: UUID
    ) -> Optional[QueryAttempt]:
        attempts = self._get_attempts_for_scene(production_id, scene_id)
        if not attempts:
            return None
        return max(attempts, key=lambda a: a.attempt_number)


query_builder_service = QueryBuilderService()