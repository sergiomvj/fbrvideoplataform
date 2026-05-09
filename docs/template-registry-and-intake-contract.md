# Template Registry & Production Intake Contract

## Template Registry

The system ships with exactly two templates, each with three variations.

### Templates

| Field | Presenter Short | VideoDoc Narrated |
|-------|----------------|-------------------|
| `type_id` | `presenter_short` | `videodoc_narrated` |
| Aspect Ratio | 9:16 | 16:9 |
| Resolution | HD | 2K |
| Max Duration | 60s | 180s |
| Max Scenes | 5 | 12 |
| Min Scenes | 1 | 2 |
| B-Roll | No | Yes |
| Asset Types | image | image, video |

### Variations (per template)

Each template has variations `1`, `2`, `3` representing controlled differences in composition.

## API Endpoints

### List Templates

```
GET /templates/
Authorization: X-User-Id header (via auth gateway)
Response: { templates: TemplateResponse[] }
```

### Get Template Detail

```
GET /templates/{template_type_id}
Authorization: X-User-Id header
Response: TemplateResponse
```

### Create Production (Intake)

```
POST /productions/
Authorization: X-User-Id header
Body: {
  title: string (required, 1-500 chars),
  template_type_id: string (required, "presenter_short" | "videodoc_narrated"),
  variation_id: string (required, "1" | "2" | "3"),
  mode: string (required, "automatic" | "manual"),
  base_content: string (optional),
  editorial_context: string (optional),
  restrictions: string[] (optional)
}
Response: ProductionResponse (201)
```

### Get Production

```
GET /productions/{production_id}
Authorization: X-User-Id header
Response: ProductionResponse
```

### List User Productions

```
GET /productions/
Authorization: X-User-Id header
Response: { productions: ProductionResponse[], count: number }
```

## Validation Rules

1. `template_type_id` must match an existing template
2. `variation_id` must be valid for the selected template
3. `mode` must be compatible with the template
4. Production is isolated by operator (`operator_user_id`)
5. All endpoints require authenticated `X-User-Id` header

## Production Response Shape

```json
{
  "id": "uuid",
  "title": "string",
  "mode": "automatic|manual",
  "template_type_id": "presenter_short|videodoc_narrated",
  "variation_id": "1|2|3",
  "current_state": "intake",
  "base_content": "string",
  "editorial_context": "string",
  "restrictions": ["string"],
  "created_at": "ISO8601",
  "updated_at": "ISO8601",
  "state_history": [{
    "from_state": "null|string",
    "to_state": "string",
    "occurred_at": "ISO8601",
    "reason": "string",
    "triggered_by": "string"
  }],
  "operator_user_id": "string"
}
```

## How Downstream Stories Consume

| Story | What It Needs | Where It Gets It |
|-------|--------------|------------------|
| 2.2 Editorial Structuring | Production in `intake` state with `base_content` | `GET /productions/{id}` then transition to `structuring` |
| 3.1 Media Sourcing | Production template + variation constraints | Template contract via `GET /templates/{type_id}` |
| 5.2 New Production Wizard | Template list + variation metadata | `GET /templates/` |
| 3.4 Manual Asset Binding | Production in `manual` mode with restrictions | `GET /productions/{id}` |

## Files

- `backend/domain/templates/contracts.py` — TemplateContract, VariationContract, constraints
- `backend/domain/templates/registry.py` — PRESENTER_SHORT, VIDEODOC_NARRATED, registry functions
- `backend/api/schemas/templates.py` — Pydantic response schemas
- `backend/api/schemas/productions.py` — Pydantic request/response schemas
- `backend/api/routes/templates.py` — Template discovery endpoints
- `backend/api/routes/productions.py` — Production CRUD + intake endpoints
