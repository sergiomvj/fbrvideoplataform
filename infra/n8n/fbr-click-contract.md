# FBR Click Integration Contract

## Overview

FBR Click is the real-time notification system that delivers push notifications and alerts to operators. This document defines the concrete integration contract for Story 6.1 compliance.

## Integration Points

### Notification Service: `integrations/fbr_click/notifier.py`

**Purpose**: Maps domain events to user notifications via FBR Click

**Supported Events**:
- `PRODUCTION_CREATED`: Welcome and setup notifications
- `PRODUCTION_HUMAN_REVIEW_REQUIRED`: Review queue alerts
- `PRODUCTION_RENDER_COMPLETED`: Delivery notifications
- `PRODUCTION_FAILED`: Failure alerts with context

**Contract Shape**:
```python
@dataclass
class FBRNotification:
    channel: str  # "production_status", "review_alerts", "system_errors"
    title: str
    message: str
    priority: str  # "low", "normal", "high", "urgent"
    user_id: str
    production_id: Optional[UUID]
    metadata: dict  # Additional context
```

### Webhook Endpoint: `/webhooks/fbr-click`

**Method**: POST
**Authentication**: API key header (`X-FBR-API-Key`)
**Content-Type**: application/json

**Request Payload**:
```json
{
  "channel": "review_alerts",
  "title": "Production Ready for Review",
  "message": "Your production 'Sample Video' has 3 scenes ready for review",
  "priority": "normal",
  "user_id": "user123",
  "production_id": "123e4567-e89b-12d3-a456-426614174000",
  "metadata": {
    "scene_count": 3,
    "template_type": "basic_video",
    "estimated_review_time": "15 minutes"
  },
  "timestamp": "2026-05-09T12:00:00Z"
}
```

**Response**: 200 OK with delivery confirmation
```json
{
  "delivered": true,
  "notification_id": "notif_456",
  "delivery_method": "push",
  "estimated_delivery": "2026-05-09T12:00:30Z"
}
```

## Notification Channels

### production_status
- Production created, structured, planned
- Status updates and progress notifications
- Non-urgent, informational

### review_alerts
- Human review required
- Review deadlines approaching
- Action-required notifications

### system_errors
- Production failures
- Integration errors
- System alerts requiring attention

## Failure Scenarios

### Escalation Paths

1. **API Unavailable**: Retry with exponential backoff, fallback to email
2. **Rate Limited**: Queue notifications, deliver when rate limit resets
3. **User Not Found**: Log error, do not block production flow
4. **Invalid Payload**: Alert development team, continue with reduced notification

### Monitoring

- Notification delivery success rate (>98%)
- Average delivery time (<10 seconds)
- User engagement rates (open rates, action rates)
- Channel-specific performance metrics

## Configuration

```bash
# Required
FBR_CLICK_API_KEY=your-api-key
FBR_CLICK_BASE_URL=https://api.fbr-click.com/v1

# Optional
FBR_CLICK_TIMEOUT_SECONDS=10
FBR_CLICK_MAX_RETRIES=3
FBR_CLICK_RATE_LIMIT_BUFFER=0.1
```

## Testing

### Notification Testing
```bash
# Send test notification
curl -X POST /api/v1/test-notifications \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "channel": "review_alerts",
    "title": "Test Notification",
    "message": "This is a test"
  }'
```