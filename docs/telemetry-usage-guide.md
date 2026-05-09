# Telemetry Usage Guide

This guide explains how to use the observability infrastructure implemented in Story 1.4 for all subsequent stories.

## Logging

### Structured Logger

All services should use the structured logger from `backend/infrastructure/logging`:

```python
from infrastructure.logging import get_logger

logger = get_logger(__name__)
```

### Adding Context

Use `LoggingContext` to add contextual identifiers to logs:

```python
from infrastructure.logging import LoggingContext

# Within a request handler
with LoggingContext(
    production_id="prod_123",
    scene_id="scene_456",
    user_id="user_789",
):
    logger.info("processing_scene", status="started")
```

Context is automatically propagated to all log calls within the context block.

### Required Identifiers

| Identifier | When to Add | Field Name |
|------------|-------------|-------------|
| production_id | Processing any production | production_id |
| scene_id | Processing a scene | scene_id |
| asset_id | Processing an asset | asset_id |
| render_job_id | Render job operations | render_job_id |
| user_id | User-initiated actions | user_id |
| organization_id | Multi-tenant operations | organization_id |
| request_id | HTTP requests | request_id |

## Audit Events

### Using the Audit Service

Import and use the audit service to record operational decisions:

```python
from domain.audit import audit_service, AuditEventType

# Recording a state change
audit_service.emit(
    event_type=AuditEventType.PRODUCTION_STATE_CHANGED,
    entity_type="production",
    entity_id="prod_123",
    before_state={"status": "draft"},
    after_state={"status": "processing"},
    actor_id="user_789",
    actor_type="user",
)

# Recording an automated decision
audit_service.emit(
    event_type=AuditEventType.DECISION_AUTO_APPROVED,
    entity_type="scene",
    entity_id="scene_456",
    metadata={"confidence": 0.95, "checks_passed": ["visual", "audio"]},
)
```

### Event Types

| Category | Events |
|----------|--------|
| Production | `production.created`, `production.state_changed` |
| Scene | `scene.created`, `scene.state_changed` |
| Asset | `asset.uploaded`, `asset.processed` |
| Render | `render_job.started`, `render_job.completed`, `render_job.failed` |
| Decision | `decision.auto_approved`, `decision.manual_review`, `decision.rejected` |
| Context Verification | `context_verification.passed`, `context_verification.failed` |
| Human Review | `human_review.completed` |

## Metrics

### Using the Metrics Collector

```python
from infrastructure.metrics import metrics_collector

# Record stage duration
metrics_collector.record_stage_duration(
    stage="context_verification",
    production_id="prod_123",
    duration=2.5
)

# Record decision outcome
metrics_collector.record_decision(
    decision_type="scene_approval",
    outcome="approved"
)

# Record integration failure
metrics_collector.record_integration_failure(
    integration="heygen",
    error_type="timeout"
)

# Record render job duration
metrics_collector.record_render_job_duration(
    render_engine="heygen",
    status="completed",
    duration=45.2
)
```

### Available Metrics

| Metric | Type | Labels | Purpose |
|--------|------|--------|---------|
| pipeline_stage_duration_seconds | Histogram | stage, production_id | Track duration of each pipeline stage |
| decision_outcome_total | Counter | decision_type, outcome | Count decision outcomes |
| integration_failure_total | Counter | integration, error_type | Track integration failures |
| render_job_duration_seconds | Histogram | render_engine, status | Track render job duration |
| active_render_jobs | Gauge | render_engine | Current active render jobs |
| context_verification_score | Histogram | check_type | Distribution of verification scores |
| human_review_duration_seconds | Histogram | review_type | Duration of human reviews |

### Viewing Metrics

Metrics are exposed at `GET /metrics` endpoint in Prometheus format. Access via:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001

## Event Taxonomy

### Naming Convention

- Use snake_case for all identifiers
- Prefix events with entity type: `{entity}.{action}`
- Use past tense for state changes: `{entity}.{state}_changed`

### Example Taxonomies

**Production Events:**
```
production.created
production.state_changed
production.deleted
```

**Scene Events:**
```
scene.created
scene.state_changed
scene.approved
scene.rejected
```

**Decision Events:**
```
decision.auto_approved
decision.manual_review
decision.rejected
```

## Security Considerations

- Never log sensitive data (passwords, tokens, PII)
- Use `request_id` for request tracing
- Context identifiers are required for production debugging
- Audit events must include actor information

## Integration with Story Dependencies

Story 1.4 blocks the following stories, which should use this telemetry infrastructure:

- **3.2 Context Verification Scoring Engine**: Use `context_verification_score` metric
- **3.3 Requery Loop**: Use `integration_failure_total` counter
- **4.3 Render Lifecycle**: Use `render_job_duration_seconds` and `active_render_jobs`
- **6.1 n8n Orchestration**: Use audit events for workflow state tracking