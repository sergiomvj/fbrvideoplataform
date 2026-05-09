from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.media_sourcing.query_strategy import (
    QueryAttempt,
    QueryStrategy,
    QueryStrategyType,
    DiagnosticCategory,
)
from infrastructure.db.models import QueryAttemptModel


class QueryAttemptRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, attempt: QueryAttempt, parent_attempt_id: str | None = None, reformulation_reason: str | None = None) -> QueryAttempt:
        model = QueryAttemptModel(
            id=str(attempt.id),
            production_id=str(attempt.production_id),
            scene_id=str(attempt.scene_id),
            brief_id=str(attempt.brief_id),
            strategy_type=attempt.strategy.strategy_type.value,
            provider_key=attempt.provider_key,
            attempt_number=attempt.attempt_number,
            query_params=json.dumps(attempt.query_params) if attempt.query_params else None,
            candidate_count=attempt.candidate_count,
            diagnostic=attempt.diagnostic.value if attempt.diagnostic else None,
            diagnostic_details=attempt.diagnostic_details,
            parent_attempt_id=parent_attempt_id,
            reformulation_reason=reformulation_reason,
            created_at=attempt.created_at,
            completed_at=attempt.completed_at,
        )
        self.session.add(model)
        await self.session.flush()
        return attempt

    async def update_result(
        self,
        attempt_id: UUID,
        candidate_count: int,
        diagnostic: str | None = None,
        diagnostic_details: str = "",
    ) -> QueryAttempt | None:
        stmt = select(QueryAttemptModel).where(QueryAttemptModel.id == str(attempt_id))
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None

        model.candidate_count = candidate_count
        model.diagnostic = diagnostic
        model.diagnostic_details = diagnostic_details
        model.completed_at = datetime.now(timezone.utc)
        await self.session.flush()
        return self._to_domain(model)

    async def get_by_id(self, attempt_id: UUID) -> QueryAttempt | None:
        stmt = select(QueryAttemptModel).where(QueryAttemptModel.id == str(attempt_id))
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def get_by_production(self, production_id: UUID) -> list[QueryAttempt]:
        stmt = (
            select(QueryAttemptModel)
            .where(QueryAttemptModel.production_id == str(production_id))
            .order_by(QueryAttemptModel.created_at)
        )
        result = await self.session.execute(stmt)
        return [self._to_domain(m) for m in result.scalars().all()]

    async def get_by_scene(self, production_id: UUID, scene_id: UUID) -> list[QueryAttempt]:
        stmt = (
            select(QueryAttemptModel)
            .where(
                QueryAttemptModel.production_id == str(production_id),
                QueryAttemptModel.scene_id == str(scene_id),
            )
            .order_by(QueryAttemptModel.attempt_number)
        )
        result = await self.session.execute(stmt)
        return [self._to_domain(m) for m in result.scalars().all()]

    async def get_latest_for_scene(self, production_id: UUID, scene_id: UUID) -> QueryAttempt | None:
        stmt = (
            select(QueryAttemptModel)
            .where(
                QueryAttemptModel.production_id == str(production_id),
                QueryAttemptModel.scene_id == str(scene_id),
            )
            .order_by(QueryAttemptModel.attempt_number.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def get_reformulation_chain(self, attempt_id: UUID) -> list[QueryAttempt]:
        chain = []
        current_id = str(attempt_id)
        while current_id:
            stmt = select(QueryAttemptModel).where(QueryAttemptModel.id == current_id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            if model is None:
                break
            chain.append(self._to_domain(model))
            current_id = model.parent_attempt_id
        return list(reversed(chain))

    def _to_domain(self, model: QueryAttemptModel) -> QueryAttempt:
        strategy = QueryStrategy(
            strategy_type=QueryStrategyType(model.strategy_type),
        )
        attempt = QueryAttempt.__new__(QueryAttempt)
        attempt.id = UUID(model.id)
        attempt.production_id = UUID(model.production_id)
        attempt.scene_id = UUID(model.scene_id)
        attempt.brief_id = UUID(model.brief_id)
        attempt.strategy = strategy
        attempt.provider_key = model.provider_key
        attempt.attempt_number = model.attempt_number
        attempt.query_params = json.loads(model.query_params) if model.query_params else {}
        attempt.candidate_count = model.candidate_count
        attempt.diagnostic = DiagnosticCategory(model.diagnostic) if model.diagnostic else None
        attempt.diagnostic_details = model.diagnostic_details or ""
        attempt.created_at = model.created_at
        attempt.completed_at = model.completed_at
        return attempt
