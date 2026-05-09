from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from domain.production.enums import ProductionMode, TemplateType, WorkflowState


@dataclass(frozen=True)
class TemplateSelection:
    template_type: TemplateType
    variation_id: str


@dataclass(frozen=True)
class AuditTimestamps:
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class StateTransition:
    from_state: WorkflowState | None
    to_state: WorkflowState
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    reason: str = ""
    triggered_by: str = ""


@dataclass
class Production:
    id: UUID = field(default_factory=uuid4)
    mode: ProductionMode = ProductionMode.AUTOMATIC
    template_selection: TemplateSelection | None = None
    current_state: WorkflowState = WorkflowState.INTAKE
    title: str = ""
    base_content: str = ""
    editorial_context: str = ""
    restrictions: list[str] = field(default_factory=list)
    audit_timestamps: AuditTimestamps = field(default_factory=AuditTimestamps)
    state_history: list[StateTransition] = field(default_factory=list)
    operator_user_id: str = ""
    organization_id: str = ""

    def __post_init__(self) -> None:
        if self.current_state == WorkflowState.INTAKE:
            self.state_history.append(
                StateTransition(
                    from_state=None,
                    to_state=WorkflowState.INTAKE,
                    reason="Production created",
                    triggered_by="system",
                )
            )

    def transition_to(
        self,
        target: WorkflowState,
        reason: str = "",
        triggered_by: str = "system",
    ) -> None:
        self._validate_transition(target)
        self.state_history.append(
            StateTransition(
                from_state=self.current_state,
                to_state=target,
                reason=reason,
                triggered_by=triggered_by,
            )
        )
        self.current_state = target
        self.audit_timestamps = AuditTimestamps(
            created_at=self.audit_timestamps.created_at,
            updated_at=datetime.now(timezone.utc),
        )

    def _validate_transition(self, target: WorkflowState) -> None:
        allowed = TRANSITIONS.get(self.current_state, set())
        if target not in allowed:
            raise InvalidTransitionError(
                f"Cannot transition from {self.current_state.value} to {target.value}"
            )

    @property
    def is_terminal(self) -> bool:
        return self.current_state in {WorkflowState.COMPLETED, WorkflowState.FAILED}

    @property
    def is_in_review(self) -> bool:
        return self.current_state == WorkflowState.HUMAN_REVIEW

    @property
    def is_in_requery(self) -> bool:
        return self.current_state == WorkflowState.REQUERY


class InvalidTransitionError(Exception):
    pass


TRANSITIONS: dict[WorkflowState, set[WorkflowState]] = {
    WorkflowState.INTAKE: {
        WorkflowState.STRUCTURING,
        WorkflowState.FAILED,
    },
    WorkflowState.STRUCTURING: {
        WorkflowState.VISUAL_PLANNING,
        WorkflowState.FAILED,
    },
    WorkflowState.VISUAL_PLANNING: {
        WorkflowState.MEDIA_SOURCING,
        WorkflowState.FAILED,
    },
    WorkflowState.MEDIA_SOURCING: {
        WorkflowState.CONTEXT_VERIFICATION,
        WorkflowState.FAILED,
    },
    WorkflowState.CONTEXT_VERIFICATION: {
        WorkflowState.HUMAN_REVIEW,
        WorkflowState.REQUERY,
        WorkflowState.COMPOSITION,
        WorkflowState.FAILED,
    },
    WorkflowState.HUMAN_REVIEW: {
        WorkflowState.COMPOSITION,
        WorkflowState.REQUERY,
        WorkflowState.FAILED,
    },
    WorkflowState.REQUERY: {
        WorkflowState.MEDIA_SOURCING,
        WorkflowState.HUMAN_REVIEW,
        WorkflowState.FAILED,
    },
    WorkflowState.COMPOSITION: {
        WorkflowState.RENDER_PENDING,
        WorkflowState.FAILED,
    },
    WorkflowState.RENDER_PENDING: {
        WorkflowState.RENDERING,
        WorkflowState.FAILED,
    },
    WorkflowState.RENDERING: {
        WorkflowState.COMPLETED,
        WorkflowState.FAILED,
    },
    WorkflowState.COMPLETED: set(),
    WorkflowState.FAILED: set(),
}
