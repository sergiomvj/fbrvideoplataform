import pytest

from domain.production.aggregate import (
    Production,
    InvalidTransitionError,
    TRANSITIONS,
)
from domain.production.enums import (
    ProductionMode,
    TemplateType,
    WorkflowState,
)
from application.services.production.workflow import ProductionWorkflowService


@pytest.fixture
def automatic_production() -> Production:
    return Production(
        mode=ProductionMode.AUTOMATIC,
        title="Test Production",
        operator_user_id="user-001",
    )


@pytest.fixture
def manual_production() -> Production:
    return Production(
        mode=ProductionMode.MANUAL,
        title="Manual Production",
        operator_user_id="user-002",
    )


@pytest.fixture
def workflow_service() -> ProductionWorkflowService:
    return ProductionWorkflowService()


class TestProductionCreation:
    def test_production_starts_at_intake(self, automatic_production: Production) -> None:
        assert automatic_production.current_state == WorkflowState.INTAKE

    def test_production_has_id(self, automatic_production: Production) -> None:
        assert automatic_production.id is not None

    def test_production_records_initial_transition(self, automatic_production: Production) -> None:
        assert len(automatic_production.state_history) == 1
        assert automatic_production.state_history[0].from_state is None
        assert automatic_production.state_history[0].to_state == WorkflowState.INTAKE

    def test_production_default_mode_is_automatic(self) -> None:
        p = Production()
        assert p.mode == ProductionMode.AUTOMATIC


class TestValidTransitions:
    def test_intake_to_structuring(self, automatic_production: Production) -> None:
        automatic_production.transition_to(WorkflowState.STRUCTURING)
        assert automatic_production.current_state == WorkflowState.STRUCTURING

    def test_full_automatic_lifecycle(self, automatic_production: Production) -> None:
        states = [
            WorkflowState.STRUCTURING,
            WorkflowState.VISUAL_PLANNING,
            WorkflowState.MEDIA_SOURCING,
            WorkflowState.CONTEXT_VERIFICATION,
            WorkflowState.COMPOSITION,
            WorkflowState.RENDER_PENDING,
            WorkflowState.RENDERING,
            WorkflowState.COMPLETED,
        ]
        for state in states:
            automatic_production.transition_to(state, reason=f"Moving to {state.value}")
        assert automatic_production.current_state == WorkflowState.COMPLETED

    def test_full_manual_lifecycle(self, manual_production: Production) -> None:
        states = [
            WorkflowState.STRUCTURING,
            WorkflowState.VISUAL_PLANNING,
            WorkflowState.MEDIA_SOURCING,
            WorkflowState.CONTEXT_VERIFICATION,
            WorkflowState.COMPOSITION,
            WorkflowState.RENDER_PENDING,
            WorkflowState.RENDERING,
            WorkflowState.COMPLETED,
        ]
        for state in states:
            manual_production.transition_to(state)
        assert manual_production.current_state == WorkflowState.COMPLETED

    def test_transition_to_human_review(self, automatic_production: Production) -> None:
        automatic_production.transition_to(WorkflowState.STRUCTURING)
        automatic_production.transition_to(WorkflowState.VISUAL_PLANNING)
        automatic_production.transition_to(WorkflowState.MEDIA_SOURCING)
        automatic_production.transition_to(WorkflowState.CONTEXT_VERIFICATION)
        automatic_production.transition_to(WorkflowState.HUMAN_REVIEW)
        assert automatic_production.is_in_review is True

    def test_transition_to_requery(self, automatic_production: Production) -> None:
        automatic_production.transition_to(WorkflowState.STRUCTURING)
        automatic_production.transition_to(WorkflowState.VISUAL_PLANNING)
        automatic_production.transition_to(WorkflowState.MEDIA_SOURCING)
        automatic_production.transition_to(WorkflowState.CONTEXT_VERIFICATION)
        automatic_production.transition_to(WorkflowState.REQUERY)
        assert automatic_production.is_in_requery is True

    def test_requery_back_to_media_sourcing(self, automatic_production: Production) -> None:
        automatic_production.transition_to(WorkflowState.STRUCTURING)
        automatic_production.transition_to(WorkflowState.VISUAL_PLANNING)
        automatic_production.transition_to(WorkflowState.MEDIA_SOURCING)
        automatic_production.transition_to(WorkflowState.CONTEXT_VERIFICATION)
        automatic_production.transition_to(WorkflowState.REQUERY)
        automatic_production.transition_to(WorkflowState.MEDIA_SOURCING)
        assert automatic_production.current_state == WorkflowState.MEDIA_SOURCING

    def test_fail_from_any_non_terminal_state(self, automatic_production: Production) -> None:
        automatic_production.transition_to(WorkflowState.STRUCTURING)
        automatic_production.transition_to(WorkflowState.FAILED, reason="Test failure")
        assert automatic_production.current_state == WorkflowState.FAILED
        assert automatic_production.is_terminal is True


class TestInvalidTransitions:
    def test_cannot_skip_states(self, automatic_production: Production) -> None:
        with pytest.raises(InvalidTransitionError):
            automatic_production.transition_to(WorkflowState.COMPOSITION)

    def test_cannot_go_backwards(self, automatic_production: Production) -> None:
        automatic_production.transition_to(WorkflowState.STRUCTURING)
        with pytest.raises(InvalidTransitionError):
            automatic_production.transition_to(WorkflowState.INTAKE)

    def test_cannot_transition_from_completed(self, automatic_production: Production) -> None:
        automatic_production.transition_to(WorkflowState.STRUCTURING)
        automatic_production.transition_to(WorkflowState.VISUAL_PLANNING)
        automatic_production.transition_to(WorkflowState.MEDIA_SOURCING)
        automatic_production.transition_to(WorkflowState.CONTEXT_VERIFICATION)
        automatic_production.transition_to(WorkflowState.COMPOSITION)
        automatic_production.transition_to(WorkflowState.RENDER_PENDING)
        automatic_production.transition_to(WorkflowState.RENDERING)
        automatic_production.transition_to(WorkflowState.COMPLETED)
        with pytest.raises(InvalidTransitionError):
            automatic_production.transition_to(WorkflowState.INTAKE)

    def test_cannot_transition_from_failed(self, automatic_production: Production) -> None:
        automatic_production.transition_to(WorkflowState.FAILED, reason="Error")
        with pytest.raises(InvalidTransitionError):
            automatic_production.transition_to(WorkflowState.INTAKE)

    def test_intake_cannot_go_to_composition(self, automatic_production: Production) -> None:
        with pytest.raises(InvalidTransitionError):
            automatic_production.transition_to(WorkflowState.COMPOSITION)


class TestStateHistory:
    def test_records_all_transitions(self, automatic_production: Production) -> None:
        automatic_production.transition_to(WorkflowState.STRUCTURING, reason="Structured")
        automatic_production.transition_to(WorkflowState.VISUAL_PLANNING, reason="Planned")
        assert len(automatic_production.state_history) == 3
        assert automatic_production.state_history[1].from_state == WorkflowState.INTAKE
        assert automatic_production.state_history[1].to_state == WorkflowState.STRUCTURING
        assert automatic_production.state_history[2].reason == "Planned"

    def test_timestamps_are_updated(self, automatic_production: Production) -> None:
        original_updated = automatic_production.audit_timestamps.updated_at
        automatic_production.transition_to(WorkflowState.STRUCTURING)
        assert automatic_production.audit_timestamps.updated_at >= original_updated
        assert automatic_production.audit_timestamps.created_at <= automatic_production.audit_timestamps.updated_at


class TestWorkflowService:
    def test_validate_transition_valid(
        self,
        automatic_production: Production,
        workflow_service: ProductionWorkflowService,
    ) -> None:
        assert workflow_service.validate_transition(
            automatic_production, WorkflowState.STRUCTURING
        ) is True

    def test_validate_transition_invalid(
        self,
        automatic_production: Production,
        workflow_service: ProductionWorkflowService,
    ) -> None:
        assert workflow_service.validate_transition(
            automatic_production, WorkflowState.COMPOSITION
        ) is False

    def test_get_allowed_transitions(
        self,
        automatic_production: Production,
        workflow_service: ProductionWorkflowService,
    ) -> None:
        allowed = workflow_service.get_allowed_transitions(automatic_production)
        assert WorkflowState.STRUCTURING in allowed
        assert WorkflowState.FAILED in allowed
        assert WorkflowState.COMPOSITION not in allowed

    def test_fail_production(
        self,
        automatic_production: Production,
        workflow_service: ProductionWorkflowService,
    ) -> None:
        workflow_service.fail_production(
            automatic_production, reason="Test", triggered_by="operator"
        )
        assert automatic_production.current_state == WorkflowState.FAILED

    def test_fail_already_failed_raises(
        self,
        automatic_production: Production,
        workflow_service: ProductionWorkflowService,
    ) -> None:
        workflow_service.fail_production(automatic_production, reason="First")
        with pytest.raises(InvalidTransitionError):
            workflow_service.fail_production(automatic_production, reason="Second")


class TestTransitionsGraph:
    def test_all_states_have_entries(self) -> None:
        for state in WorkflowState:
            assert state in TRANSITIONS

    def test_terminal_states_have_no_exits(self) -> None:
        assert len(TRANSITIONS[WorkflowState.COMPLETED]) == 0
        assert len(TRANSITIONS[WorkflowState.FAILED]) == 0

    def test_all_non_terminal_states_can_fail(self) -> None:
        for state, targets in TRANSITIONS.items():
            if state not in {WorkflowState.COMPLETED, WorkflowState.FAILED}:
                assert WorkflowState.FAILED in targets, (
                    f"State {state.value} cannot transition to FAILED"
                )
