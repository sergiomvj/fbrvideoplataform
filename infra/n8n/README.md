# n8n Integration Assets

This directory contains the concrete n8n integration artifacts and workflow bootstrap assets for Story 6.1 compliance.

## Overview

n8n is the orchestration platform that coordinates complex workflows involving multiple systems. This directory provides the runtime artifacts needed to make Story 6.1's orchestration promises concrete.

## Workflow Assets

### Event-Driven Workflows

#### Production Lifecycle Workflow (`production-lifecycle.json`)
- **Triggers**: `PRODUCTION_CREATED`, `PRODUCTION_STRUCTURED`, `PRODUCTION_VISUAL_PLANNED`
- **Actions**: Notification routing, status updates, automated quality checks
- **Payload Example**:
```json
{
  "event_type": "PRODUCTION_CREATED",
  "production_id": "123e4567-e89b-12d3-a456-426614174000",
  "payload": {
    "title": "Sample Production",
    "mode": "automatic",
    "template_type_id": "basic_video"
  },
  "timestamp": "2026-05-09T12:00:00Z"
}
```

#### Media Processing Workflow (`media-processing.json`)
- **Triggers**: `PRODUCTION_MEDIA_SOURCING`, `PRODUCTION_HUMAN_REVIEW_REQUIRED`
- **Actions**: Asset validation, metadata enrichment, review queue population
- **Payload Example**:
```json
{
  "event_type": "PRODUCTION_MEDIA_SOURCING",
  "production_id": "123e4567-e89b-12d3-a456-426614174000",
  "payload": {
    "scene_count": 3,
    "required_assets": ["video", "image", "audio"]
  }
}
```

#### Render Pipeline Workflow (`render-pipeline.json`)
- **Triggers**: `PRODUCTION_RENDER_COMPLETED`, `PRODUCTION_RENDER_FAILED`
- **Actions**: Distribution, archiving, error recovery
- **Payload Example**:
```json
{
  "event_type": "PRODUCTION_RENDER_COMPLETED",
  "production_id": "123e4567-e89b-12d3-a456-426614174000",
  "payload": {
    "render_url": "https://cdn.example.com/renders/prod123.mp4",
    "duration_seconds": 120,
    "file_size_mb": 45.2
  }
}
```

## Integration Points

### Webhook Endpoints

#### OpenClaw Assistant Integration
- **Endpoint**: `POST /webhooks/openclaw`
- **Purpose**: AI assistant notifications and context updates
- **Contract**: See `backend/integrations/openclaw/hooks.py`
- **Example Payload**:
```json
{
  "event_type": "PRODUCTION_HUMAN_REVIEW_REQUIRED",
  "production_id": "123e4567-e89b-12d3-a456-426614174000",
  "context": {
    "scene_count": 5,
    "issues_found": ["low_confidence_score", "missing_asset"]
  }
}
```

#### FBR Click Notification System
- **Endpoint**: `POST /webhooks/fbr-click`
- **Purpose**: Real-time user notifications via FBR Click
- **Contract**: See `backend/integrations/fbr_click/notifier.py`
- **Example Payload**:
```json
{
  "channel": "production_status",
  "title": "Production Ready for Review",
  "message": "Your production 'Sample Video' is ready for human review",
  "priority": "normal",
  "user_id": "user123",
  "production_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

## Deployment Configuration

### Environment Variables

```bash
# n8n Webhook URLs (configured in n8n workflows)
N8N_WEBHOOK_BASE_URL=https://your-n8n-instance.com/webhook

# OpenClaw Configuration
OPENCLAW_WEBHOOK_URL=https://your-app.com/webhooks/openclaw
OPENCLAW_API_KEY=your-openclaw-key

# FBR Click Configuration
FBR_CLICK_API_KEY=your-fbr-click-key
FBR_CLICK_WEBHOOK_URL=https://your-app.com/webhooks/fbr-click
```

### n8n Workflow Import

1. Access your n8n instance admin panel
2. Import workflows from this directory:
   - `production-lifecycle.json`
   - `media-processing.json`
   - `render-pipeline.json`
3. Configure webhook URLs to match your deployment
4. Activate workflows

## Failure Handling

### Escalation Paths

1. **Event Delivery Failures**: Retry with exponential backoff, alert on final failure
2. **Webhook Timeouts**: Circuit breaker pattern, fallback to email notifications
3. **Integration Errors**: Log structured errors, trigger manual intervention workflows

### Monitoring

- Event delivery success rates
- Webhook response times
- Integration health checks
- Error rate thresholds

## Security Considerations

- All webhook endpoints require authentication tokens
- Payloads contain only necessary production metadata
- No sensitive credentials transmitted via workflows
- Audit logging for all orchestration activities

## Testing

### Workflow Testing
```bash
# Test event emission
curl -X POST /api/v1/productions/test-event \
  -H "Content-Type: application/json" \
  -d '{"event_type": "PRODUCTION_CREATED", "payload": {"test": true}}'

# Verify webhook delivery (check n8n logs)
# Verify OpenClaw/FBR notifications
```

### Integration Testing
```bash
# Full pipeline test
npm run test:integration:n8n

# Webhook endpoint tests
npm run test:webhooks
```