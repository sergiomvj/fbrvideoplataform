from __future__ import annotations

from uuid import UUID

from domain.production.aggregate import Production, InvalidTransitionError
from domain.production.enums import WorkflowState


class ProductionWorkflowService:
    def validate_transition(
        self, production: Production, target: WorkflowState
    ) -> bool:
        try:
            production._validate_transition(target)
            return True
        except InvalidTransitionError:
            return False

    def get_allowed_transitions(self, production: Production) -> set[WorkflowState]:
        from domain.production.aggregate import TRANSITIONS

        return TRANSITIONS.get(production.current_state, set())

    def transition(
        self,
        production: Production,
        target: WorkflowState,
        reason: str = "",
        triggered_by: str = "system",
    ) -> None:
        production.transition_to(target, reason=reason, triggered_by=triggered_by)

    def fail_production(
        self,
        production: Production,
        reason: str,
        triggered_by: str = "system",
    ) -> None:
        if production.is_terminal:
            raise InvalidTransitionError(
                f"Production is already in terminal state: {production.current_state.value}"
            )
        production.transition_to(
            WorkflowState.FAILED, reason=reason, triggered_by=triggered_by
        )
