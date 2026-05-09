# PostgreSQL Schema — Initial Bootstrap (Story 7.9)

## File

`001_initial_schema.sql`

## Table Creation Order

Tables must be created in this order due to foreign key dependencies:

| Layer | Tables | Notes |
|-------|--------|-------|
| 1 — Identity | `organizations` | No FK deps |
| 2 — Users | `users` | FK → `organizations` |
| 3 — Templates | `templates` | No FK deps |
| 4 — Template Variations | `template_variations` | FK → `templates` |
| 5 — Productions | `productions` | FK → `organizations`, `users`, `templates` |
| 6 — Production Sub-tables | `production_restrictions`, `production_state_transitions` | FK → `productions` |
| 7 — Narrative | `narrative_bases` → `narrative_blocks` | FK → `productions`, `narrative_bases` |
| 8 — Visual Briefs | `visual_briefs` | FK → `productions`, `narrative_blocks` |
| 9 — Assets & Scoring | `asset_candidates` → `verification_scores` | FK → `productions`, `narrative_blocks`, `asset_candidates` |
| 10 — Review | `review_queue_items` | FK → `productions`, `narrative_blocks`, `asset_candidates`, `verification_scores` |
| 11 — Manual Bindings | `manual_bindings` | FK → `productions`, `narrative_blocks`, `users` |
| 12 — Composition | `compositions` → `composition_slots` | FK → `productions`, `templates`, `manual_bindings` |
| 13 — Render | `render_jobs` → `render_job_events` | FK → `productions`, `compositions`, `render_jobs` |
| 14 — Audit | `audit_events` | FK → `productions`, `users` |

## Current-State vs Append-Only History

### Current-State Tables
These hold the active operational snapshot and are updated in place:

- `organizations`
- `users`
- `templates`
- `template_variations`
- `productions`
- `production_restrictions`
- `narrative_bases`
- `narrative_blocks`
- `visual_briefs`
- `asset_candidates`
- `review_queue_items`
- `manual_bindings`
- `compositions`
- `composition_slots`
- `render_jobs`

### Append-Only History Tables
These are never updated or deleted — only inserted into:

- `production_state_transitions` — workflow state history
- `verification_scores` — scoring decisions log
- `render_job_events` — render lifecycle events
- `audit_events` — compliance audit trail

## Story-to-Table Mapping

| Story | Tables Adopted |
|-------|----------------|
| 7.1–7.2 (Production Core) | `organizations`, `users`, `productions`, `production_restrictions`, `production_state_transitions` |
| 7.3–7.4 (Templates) | `templates`, `template_variations` |
| 7.5 (Narrative) | `narrative_bases`, `narrative_blocks` |
| 7.6 (Visual Brief) | `visual_briefs` |
| 7.7 (Asset Sourcing & Verification) | `asset_candidates`, `verification_scores` |
| 7.8 (Review Queue) | `review_queue_items` |
| 7.9 (Schema Bootstrap) | All tables (this migration) |
| 7.10 (Manual Bindings) | `manual_bindings` |
| 7.11 (Composition) | `compositions`, `composition_slots` |
| 7.12 (Render) | `render_jobs`, `render_job_events` |
| 7.13 (Audit) | `audit_events` |

## How to Run

```bash
psql -h <host> -U <user> -d <database> -f infra/postgres/schema/001_initial_schema.sql
```

Or via Docker:

```bash
docker exec -i <postgres-container> psql -U <user> -d <database> < infra/postgres/schema/001_initial_schema.sql
```

The migration is wrapped in a transaction (`BEGIN`/`COMMIT`) — it will succeed entirely or fail without partial changes.
