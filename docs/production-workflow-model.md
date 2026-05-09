# Production Workflow Model

## Overview

The production domain model defines the central aggregate and its lifecycle state machine. All downstream modules (editorial, media, composition, render) integrate through this shared workflow.

## Workflow States

```
INTAKE → STRUCTURING → VISUAL_PLANNING → MEDIA_SOURCING → CONTEXT_VERIFICATION
                                                                      │
                                                        ┌─────────────┤
                                                        │             │
                                                   HUMAN_REVIEW   REQUERY
                                                        │             │
                                                        │             ↓
                                                        │      MEDIA_SOURCING (loop)
                                                        │
                                                        ↓
                                                   COMPOSITION → RENDER_PENDING → RENDERING → COMPLETED
                                                                                              or
                                                                                          FAILED (from any state)
```

### State Descriptions

| State | Description | Module Owner |
|-------|-------------|--------------|
| `intake` | Production created, awaiting structuring | Intake API |
| `structuring` | Content being structured into scenes/blocks | Editorial Engine |
| `visual_planning` | Generating visual briefs per scene | Visual Planning |
| `media_sourcing` | Obtaining candidate media assets | Media Sourcing |
| `context_verification` | Scoring candidate aderencia contextual | Context Verification |
| `human_review` | Awaiting human operator review | Human Review |
| `requery` | Re-obtaining media after low score | Media Sourcing (retry) |
| `composition` | Assembling final piece from template + assets | Composition Engine |
| `render_pending` | Composition ready, awaiting render dispatch | Render Orchestration |
| `rendering` | External render in progress | Render Orchestration |
| `completed` | Production finished successfully | — |
| `failed` | Production failed (any stage) | — |

## Production Modes

Both modes share the **same** state machine and the **same** final composition logic:

- **Automatic (`automatic`)**: System drives structuring, briefs, sourcing and scoring. Human review only when score is 60-89.
- **Manual (`manual`)**: Operator provides assets directly. System validates compatibility and assembles.

The mode is set at creation time and recorded on the `Production` aggregate. Downstream modules may branch behavior based on mode but must not create parallel lifecycle paths.

## Domain Objects

### Production (Aggregate Root)

```python
@dataclass
class Production:
    id: UUID
    mode: ProductionMode                  # automatic | manual
    template_selection: TemplateSelection  # template type + variation
    current_state: WorkflowState
    title: str
    base_content: str                     # article/text/script
    editorial_context: str
    restrictions: list[str]
    audit_timestamps: AuditTimestamps     # created_at, updated_at
    state_history: list[StateTransition]  # full audit trail
    operator_user_id: str
    organization_id: str
```

### TemplateSelection (Value Object)

```python
@dataclass(frozen=True)
class TemplateSelection:
    template_type: TemplateType  # presenter_short | videodoc_narrated
    variation_id: str            # "1", "2", or "3"
```

### StateTransition (Event Record)

```python
@dataclass
class StateTransition:
    from_state: WorkflowState | None
    to_state: WorkflowState
    occurred_at: datetime
    reason: str
    triggered_by: str            # "system", "operator", "n8n", etc.
```

## Transition Rules

1. Transitions are explicit — no state can be inferred from UI or route logic
2. `InvalidTransitionError` is raised for illegal transitions
3. Every transition is recorded in `state_history` with timestamp, reason and trigger source
4. `FAILED` is reachable from any non-terminal state
5. `COMPLETED` and `FAILED` are terminal — no further transitions allowed

## How Downstream Stories Plug In

| Story | States Consumed | States Produced |
|-------|----------------|-----------------|
| 2.1 Intake APIs | `intake` | `intake` (creates production) |
| 2.2 Editorial Structuring | `intake` → `structuring` | `structuring` → `visual_planning` |
| 2.3 Visual Planning | `structuring` → `visual_planning` | `visual_planning` → `media_sourcing` |
| 3.1 Media Sourcing | `visual_planning` → `media_sourcing` | `media_sourcing` → `context_verification` |
| 3.2 Context Verification | `media_sourcing` → `context_verification` | `context_verification` → `human_review` or `requery` or `composition` |
| 3.3 Requery Loop | `context_verification` → `requery` | `requery` → `media_sourcing` |
| 3.4 Human Review | `human_review` | `human_review` → `composition` or `requery` |
| 4.1/4.2 Composition | `composition` | `composition` → `render_pending` |
| 4.3 Render Orchestration | `render_pending` → `rendering` | `rendering` → `completed` |

## API Usage

```python
from domain.production import Production, WorkflowState, ProductionMode

# Create
production = Production(
    mode=ProductionMode.AUTOMATIC,
    title="Breaking News Video",
    operator_user_id="user-123",
)

# Transition
production.transition_to(
    WorkflowState.STRUCTURING,
    reason="Starting editorial structuring",
    triggered_by="system",
)

# Check state
assert not production.is_terminal
assert production.current_state == WorkflowState.STRUCTURING
```

## Files

- `backend/domain/production/enums.py` — Enums: ProductionMode, TemplateType, WorkflowState
- `backend/domain/production/aggregate.py` — Production aggregate, value objects, TRANSITIONS map
- `backend/application/services/production/workflow.py` — ProductionWorkflowService
- `backend/tests/test_production_workflow.py` — 26 unit tests covering all transitions
