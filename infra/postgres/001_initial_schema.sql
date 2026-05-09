CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE users (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    email text NOT NULL UNIQUE,
    display_name text NOT NULL,
    status text NOT NULL DEFAULT 'active',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE organizations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name text NOT NULL,
    slug text NOT NULL UNIQUE,
    status text NOT NULL DEFAULT 'active',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE organization_memberships (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id uuid NOT NULL REFERENCES organizations(id),
    user_id uuid NOT NULL REFERENCES users(id),
    role text NOT NULL,
    status text NOT NULL DEFAULT 'active',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (organization_id, user_id)
);

CREATE TABLE template_types (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    type_key text NOT NULL UNIQUE,
    name text NOT NULL,
    description text,
    aspect_ratio text NOT NULL,
    resolution text NOT NULL,
    max_duration_seconds integer NOT NULL CHECK (max_duration_seconds > 0),
    min_scenes integer NOT NULL CHECK (min_scenes >= 0),
    max_scenes integer NOT NULL CHECK (max_scenes >= min_scenes),
    supports_broll boolean NOT NULL DEFAULT false,
    status text NOT NULL DEFAULT 'active',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE template_variations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    template_type_id uuid NOT NULL REFERENCES template_types(id),
    variation_key text NOT NULL,
    label text NOT NULL,
    description text,
    status text NOT NULL DEFAULT 'active',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (template_type_id, variation_key)
);

CREATE TABLE organization_template_profiles (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id uuid NOT NULL REFERENCES organizations(id),
    template_type_id uuid NOT NULL REFERENCES template_types(id),
    default_variation_id uuid REFERENCES template_variations(id),
    default_avatar_ref text,
    default_background_ref text,
    editorial_style jsonb NOT NULL DEFAULT '{}'::jsonb,
    restrictions jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE productions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id uuid NOT NULL REFERENCES organizations(id),
    operator_user_id uuid NOT NULL REFERENCES users(id),
    mode text NOT NULL CHECK (mode IN ('automatic', 'manual')),
    current_state text NOT NULL,
    template_type_id uuid NOT NULL REFERENCES template_types(id),
    template_variation_id uuid NOT NULL REFERENCES template_variations(id),
    title text NOT NULL,
    base_content text,
    editorial_context text,
    restrictions text,
    source_type text,
    priority text NOT NULL DEFAULT 'normal',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    deleted_at timestamptz
);

CREATE INDEX idx_productions_org_created ON productions (organization_id, created_at DESC);
CREATE INDEX idx_productions_operator_created ON productions (operator_user_id, created_at DESC);
CREATE INDEX idx_productions_state ON productions (current_state);

CREATE TABLE production_inputs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    production_id uuid NOT NULL REFERENCES productions(id) ON DELETE CASCADE,
    input_type text NOT NULL,
    input_payload jsonb NOT NULL,
    submitted_by_user_id uuid REFERENCES users(id),
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE production_state_transitions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    production_id uuid NOT NULL REFERENCES productions(id) ON DELETE CASCADE,
    from_state text,
    to_state text NOT NULL,
    reason text,
    triggered_by_type text NOT NULL,
    triggered_by_user_id uuid REFERENCES users(id),
    triggered_by_system text,
    trace_id uuid,
    occurred_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_production_state_transitions_prod_time
    ON production_state_transitions (production_id, occurred_at);

CREATE TABLE production_failures (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    production_id uuid NOT NULL REFERENCES productions(id) ON DELETE CASCADE,
    failure_type text NOT NULL,
    stage text NOT NULL,
    message text NOT NULL,
    details jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE narrative_structures (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    production_id uuid NOT NULL REFERENCES productions(id) ON DELETE CASCADE,
    version integer NOT NULL,
    objective text,
    target_duration_seconds integer,
    total_duration_seconds integer,
    status text NOT NULL,
    generated_by_type text NOT NULL,
    generated_by_user_id uuid REFERENCES users(id),
    generated_by_system text,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (production_id, version)
);

CREATE TABLE narrative_blocks (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    narrative_structure_id uuid NOT NULL REFERENCES narrative_structures(id) ON DELETE CASCADE,
    scene_index integer NOT NULL CHECK (scene_index >= 0),
    narrative_role text NOT NULL,
    text_content text NOT NULL,
    estimated_duration_seconds integer NOT NULL CHECK (estimated_duration_seconds >= 0),
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_narrative_blocks_structure_scene
    ON narrative_blocks (narrative_structure_id, scene_index);

CREATE TABLE scene_visual_briefs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    production_id uuid NOT NULL REFERENCES productions(id) ON DELETE CASCADE,
    narrative_block_id uuid NOT NULL REFERENCES narrative_blocks(id) ON DELETE CASCADE,
    version integer NOT NULL,
    theme text NOT NULL,
    visual_function text NOT NULL,
    visible_subject text NOT NULL,
    geo_cultural_context text,
    time_period text,
    editorial_tone text,
    literalness_level text NOT NULL,
    allowed_elements jsonb NOT NULL DEFAULT '[]'::jsonb,
    forbidden_elements jsonb NOT NULL DEFAULT '[]'::jsonb,
    preferred_asset_type text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_scene_visual_briefs_prod_block
    ON scene_visual_briefs (production_id, narrative_block_id);

CREATE TABLE media_sources (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    source_key text NOT NULL UNIQUE,
    name text NOT NULL,
    source_type text NOT NULL,
    status text NOT NULL DEFAULT 'active',
    config jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE media_query_attempts (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    production_id uuid NOT NULL REFERENCES productions(id) ON DELETE CASCADE,
    scene_visual_brief_id uuid NOT NULL REFERENCES scene_visual_briefs(id) ON DELETE CASCADE,
    attempt_number integer NOT NULL CHECK (attempt_number > 0),
    source_id uuid NOT NULL REFERENCES media_sources(id),
    query_strategy text NOT NULL,
    query_payload jsonb NOT NULL,
    diagnostic_reason text,
    triggered_by text NOT NULL,
    started_at timestamptz NOT NULL DEFAULT now(),
    finished_at timestamptz,
    status text NOT NULL
);

CREATE INDEX idx_media_query_attempts_prod_brief_attempt
    ON media_query_attempts (production_id, scene_visual_brief_id, attempt_number);

CREATE TABLE asset_candidates (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    production_id uuid NOT NULL REFERENCES productions(id) ON DELETE CASCADE,
    scene_visual_brief_id uuid NOT NULL REFERENCES scene_visual_briefs(id) ON DELETE CASCADE,
    query_attempt_id uuid NOT NULL REFERENCES media_query_attempts(id) ON DELETE CASCADE,
    source_id uuid NOT NULL REFERENCES media_sources(id),
    external_asset_id text NOT NULL,
    media_type text NOT NULL,
    asset_url text NOT NULL,
    thumbnail_url text,
    title text,
    description text,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_asset_candidates_prod_brief
    ON asset_candidates (production_id, scene_visual_brief_id);

CREATE INDEX idx_asset_candidates_source_external
    ON asset_candidates (source_id, external_asset_id);

CREATE TABLE asset_score_runs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    production_id uuid NOT NULL REFERENCES productions(id) ON DELETE CASCADE,
    asset_candidate_id uuid NOT NULL REFERENCES asset_candidates(id) ON DELETE CASCADE,
    scene_visual_brief_id uuid NOT NULL REFERENCES scene_visual_briefs(id) ON DELETE CASCADE,
    scoring_model text NOT NULL,
    scoring_version text NOT NULL,
    final_score numeric(5,2) NOT NULL CHECK (final_score >= 0 AND final_score <= 100),
    decision_band text NOT NULL,
    short_justification text,
    conflict_flags jsonb NOT NULL DEFAULT '[]'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_asset_score_runs_prod_candidate
    ON asset_score_runs (production_id, asset_candidate_id);

CREATE TABLE asset_score_breakdowns (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_score_run_id uuid NOT NULL REFERENCES asset_score_runs(id) ON DELETE CASCADE,
    criterion_key text NOT NULL,
    weight numeric(5,2) NOT NULL,
    score numeric(5,2) NOT NULL,
    explanation text,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_asset_score_breakdowns_run_criterion
    ON asset_score_breakdowns (asset_score_run_id, criterion_key);

CREATE TABLE asset_decisions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    production_id uuid NOT NULL REFERENCES productions(id) ON DELETE CASCADE,
    scene_visual_brief_id uuid NOT NULL REFERENCES scene_visual_briefs(id) ON DELETE CASCADE,
    asset_candidate_id uuid NOT NULL REFERENCES asset_candidates(id) ON DELETE CASCADE,
    asset_score_run_id uuid REFERENCES asset_score_runs(id),
    decision_status text NOT NULL,
    decision_origin text NOT NULL,
    is_current boolean NOT NULL DEFAULT true,
    decided_by_user_id uuid REFERENCES users(id),
    decided_by_system text,
    decided_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_asset_decisions_scene_time
    ON asset_decisions (scene_visual_brief_id, decided_at DESC);

CREATE UNIQUE INDEX uq_asset_decisions_current_scene
    ON asset_decisions (scene_visual_brief_id)
    WHERE is_current = true
      AND decision_status IN ('auto_approved', 'human_approved', 'manual_fixed');

CREATE TABLE asset_decision_events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_decision_id uuid NOT NULL REFERENCES asset_decisions(id) ON DELETE CASCADE,
    previous_status text,
    new_status text NOT NULL,
    reason text,
    actor_type text NOT NULL,
    actor_user_id uuid REFERENCES users(id),
    actor_system text,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE review_queue_items (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    production_id uuid NOT NULL REFERENCES productions(id) ON DELETE CASCADE,
    scene_visual_brief_id uuid NOT NULL REFERENCES scene_visual_briefs(id) ON DELETE CASCADE,
    asset_candidate_id uuid NOT NULL REFERENCES asset_candidates(id) ON DELETE CASCADE,
    asset_score_run_id uuid REFERENCES asset_score_runs(id),
    status text NOT NULL CHECK (
        status IN ('pending', 'approved', 'rejected', 'requery_requested', 'resolved')
    ),
    priority text NOT NULL DEFAULT 'normal',
    assigned_to_user_id uuid REFERENCES users(id),
    enqueued_at timestamptz NOT NULL DEFAULT now(),
    resolved_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_review_queue_status_priority_time
    ON review_queue_items (status, priority, enqueued_at);

CREATE INDEX idx_review_queue_prod_status
    ON review_queue_items (production_id, status);

CREATE TABLE review_actions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    review_queue_item_id uuid NOT NULL REFERENCES review_queue_items(id) ON DELETE CASCADE,
    action_type text NOT NULL,
    performed_by_user_id uuid NOT NULL REFERENCES users(id),
    comment text,
    payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE manual_asset_bindings (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    production_id uuid NOT NULL REFERENCES productions(id) ON DELETE CASCADE,
    scene_visual_brief_id uuid NOT NULL REFERENCES scene_visual_briefs(id) ON DELETE CASCADE,
    narrative_block_id uuid REFERENCES narrative_blocks(id),
    asset_candidate_id uuid REFERENCES asset_candidates(id),
    binding_type text NOT NULL CHECK (
        binding_type IN ('required', 'fixed', 'prohibited', 'preferred')
    ),
    asset_url text NOT NULL,
    asset_title text,
    status text NOT NULL DEFAULT 'active',
    bound_by_user_id uuid NOT NULL REFERENCES users(id),
    template_type_id uuid REFERENCES template_types(id),
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_manual_asset_bindings_prod_scene_status
    ON manual_asset_bindings (production_id, scene_visual_brief_id, status);

CREATE TABLE manual_binding_events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    manual_asset_binding_id uuid NOT NULL REFERENCES manual_asset_bindings(id) ON DELETE CASCADE,
    event_type text NOT NULL,
    actor_user_id uuid REFERENCES users(id),
    details jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE production_compositions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    production_id uuid NOT NULL REFERENCES productions(id) ON DELETE CASCADE,
    template_type_id uuid NOT NULL REFERENCES template_types(id),
    template_variation_id uuid NOT NULL REFERENCES template_variations(id),
    version integer NOT NULL,
    status text NOT NULL,
    narration_text text,
    timeline_payload jsonb NOT NULL,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (production_id, version)
);

CREATE TABLE composition_slots (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    composition_id uuid NOT NULL REFERENCES production_compositions(id) ON DELETE CASCADE,
    slot_index integer NOT NULL CHECK (slot_index >= 0),
    slot_type text NOT NULL,
    duration_seconds integer NOT NULL CHECK (duration_seconds >= 0),
    content_ref text,
    scene_visual_brief_id uuid REFERENCES scene_visual_briefs(id),
    asset_candidate_id uuid REFERENCES asset_candidates(id),
    manual_asset_binding_id uuid REFERENCES manual_asset_bindings(id),
    payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_composition_slots_comp_slot
    ON composition_slots (composition_id, slot_index);

CREATE TABLE render_jobs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    production_id uuid NOT NULL REFERENCES productions(id) ON DELETE CASCADE,
    composition_id uuid NOT NULL REFERENCES production_compositions(id) ON DELETE CASCADE,
    provider_key text NOT NULL,
    external_job_id text,
    status text NOT NULL CHECK (
        status IN ('queued', 'processing', 'completed', 'failed', 'cancelled')
    ),
    submitted_by_type text NOT NULL,
    submitted_by_user_id uuid REFERENCES users(id),
    progress_percent numeric(5,2),
    output_url text,
    error_message text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_render_jobs_prod_created
    ON render_jobs (production_id, created_at DESC);

CREATE INDEX idx_render_jobs_provider_external
    ON render_jobs (provider_key, external_job_id);

CREATE TABLE render_job_events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    render_job_id uuid NOT NULL REFERENCES render_jobs(id) ON DELETE CASCADE,
    previous_status text,
    new_status text NOT NULL,
    provider_payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    error_message text,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE domain_events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type text NOT NULL,
    production_id uuid REFERENCES productions(id),
    entity_type text NOT NULL,
    entity_id uuid,
    payload jsonb NOT NULL,
    source text NOT NULL,
    trace_id uuid,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_domain_events_prod_created
    ON domain_events (production_id, created_at);

CREATE INDEX idx_domain_events_type_created
    ON domain_events (event_type, created_at);

CREATE TABLE audit_events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id uuid REFERENCES organizations(id),
    production_id uuid REFERENCES productions(id),
    entity_type text NOT NULL,
    entity_id text NOT NULL,
    event_type text NOT NULL,
    actor_type text NOT NULL,
    actor_user_id uuid REFERENCES users(id),
    before_state jsonb,
    after_state jsonb,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    trace_id uuid,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_audit_events_prod_created
    ON audit_events (production_id, created_at DESC);

CREATE INDEX idx_audit_events_actor_created
    ON audit_events (actor_user_id, created_at DESC);

CREATE INDEX idx_audit_events_entity_created
    ON audit_events (entity_type, entity_id, created_at DESC);

CREATE TABLE integration_request_logs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    production_id uuid REFERENCES productions(id),
    integration_key text NOT NULL,
    operation_key text NOT NULL,
    request_payload jsonb NOT NULL,
    response_payload jsonb,
    http_status integer,
    status text NOT NULL,
    started_at timestamptz NOT NULL DEFAULT now(),
    finished_at timestamptz,
    trace_id uuid
);

CREATE INDEX idx_integration_request_logs_integration_started
    ON integration_request_logs (integration_key, started_at DESC);

CREATE INDEX idx_integration_request_logs_prod_started
    ON integration_request_logs (production_id, started_at DESC);

CREATE TABLE llm_execution_logs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    production_id uuid REFERENCES productions(id),
    purpose text NOT NULL,
    provider text NOT NULL,
    model text NOT NULL,
    input_hash text NOT NULL,
    input_payload jsonb NOT NULL,
    output_payload jsonb,
    status text NOT NULL,
    latency_ms integer,
    token_usage jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);
