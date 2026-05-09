# OpenClaw Integration Contract

## Overview

OpenClaw is the AI assistant system that provides contextual help and automation suggestions to operators. This document defines the concrete integration contract for Story 6.1 compliance.

## Integration Points

### Event Hook: `integrations/openclaw/hooks.py`

**Purpose**: Translates domain events into OpenClaw-compatible notifications

**Supported Events**:
- `PRODUCTION_HUMAN_REVIEW_REQUIRED`: Notifies assistant about review needs
- `PRODUCTION_FAILED`: Escalates failures to assistant attention
- `PRODUCTION_COMPLETED`: Provides completion context

**Contract Shape**:
```python
@dataclass
class OpenClawNotification:
    event_type: str
    production_id: UUID
    context: dict  # Event-specific context data
    priority: str  # "low", "normal", "high", "critical"
    requires_action: bool
```

### Webhook Endpoint: `/webhooks/openclaw`

**Method**: POST
**Authentication**: Bearer token (`OPENCLAW_WEBHOOK_TOKEN`)
**Content-Type**: application/json

**Request Payload**:
```json
{
  "event_type": "PRODUCTION_HUMAN_REVIEW_REQUIRED",
  "production_id": "123e4567-e89b-12d3-a456-426614174000",
  "context": {
    "scene_count": 5,
    "issues_found": ["low_confidence_score", "missing_asset"],
    "operator_id": "user123",
    "template_type": "basic_video"
  },
  "priority": "normal",
  "requires_action": true,
  "timestamp": "2026-05-09T12:00:00Z"
}
```

**Response**: 200 OK with optional suggestions
```json
{
  "acknowledged": true,
  "suggestions": [
    "Consider manual asset binding for scene 2",
    "Review scoring thresholds for this template type"
  ]
}
```

## Failure Scenarios

### Escalation Paths

1. **Webhook Unavailable**: Retry 3 times with 30s intervals, then log and continue
2. **Authentication Failure**: Alert security team, disable OpenClaw integration
3. **Response Timeout**: Treat as successful (fire-and-forget for non-critical events)

### Monitoring

- Webhook delivery success rate (>95%)
- Response time (<5 seconds average)
- Error rate by event type
- Assistant suggestion acceptance rate

## Configuration

```bash
# Required
OPENCLAW_WEBHOOK_URL=https://openclaw-api.example.com/webhooks/synkra
OPENCLAW_WEBHOOK_TOKEN=your-webhook-token

# Optional
OPENCLAW_TIMEOUT_SECONDS=30
OPENCLAW_RETRY_ATTEMPTS=3
```