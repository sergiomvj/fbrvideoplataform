CREATE EXTENSION IF NOT EXISTS "pgcrypto";

BEGIN;

CREATE TABLE organizations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR NOT NULL,
    slug VARCHAR NOT NULL UNIQUE,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE users (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id uuid NOT NULL REFERENCES organizations(id),
    username VARCHAR NOT NULL UNIQUE,
    display_name VARCHAR,
    role VARCHAR NOT NULL DEFAULT 'operator',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE templates (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR NOT NULL,
    description TEXT,
    aspect_ratio VARCHAR NOT NULL,
    resolution VARCHAR NOT NULL,
    max_duration_seconds INT NOT NULL,
    max_scenes INT NOT NULL,
    min_scenes INT NOT NULL,
    supports_broll BOOLEAN NOT NULL DEFAULT false,
    supported_asset_types VARCHAR[] NOT NULL,
    compatible_modes VARCHAR[] NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE template_variations (
    template_id VARCHAR(50) NOT NULL REFERENCES templates(id),
    variation_id VARCHAR(10) NOT NULL,
    label VARCHAR NOT NULL,
    description TEXT,
    compatible_modes VARCHAR[] NOT NULL,
    PRIMARY KEY (template_id, variation_id)
);

CREATE TABLE productions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id uuid NOT NULL REFERENCES organizations(id),
    operator_user_id uuid NOT NULL REFERENCES users(id),
    mode VARCHAR(20) NOT NULL CHECK (mode IN ('automatic', 'manual')),
    template_type_id VARCHAR(50) NOT NULL REFERENCES templates(id),
    variation_id VARCHAR(10),
    title VARCHAR(500) NOT NULL,
    base_content TEXT,
    editorial_context TEXT,
    current_state VARCHAR(30) NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE production_restrictions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    production_id uuid NOT NULL REFERENCES productions(id) ON DELETE CASCADE,
    restriction TEXT NOT NULL
);

CREATE TABLE production_state_transitions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    production_id uuid NOT NULL REFERENCES productions(id) ON DELETE CASCADE,
    from_state VARCHAR(30),
    to_state VARCHAR(30) NOT NULL,
    reason TEXT,
    triggered_by VARCHAR(50) NOT NULL,
    occurred_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE narrative_bases (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    production_id uuid NOT NULL REFERENCES productions(id) ON DELETE CASCADE,
    objective TEXT,
    target_duration_seconds FLOAT,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE narrative_blocks (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    narrative_base_id uuid NOT NULL REFERENCES narrative_bases(id) ON DELETE CASCADE,
    scene_index INT NOT NULL,
    role VARCHAR(30) NOT NULL,
    text TEXT NOT NULL,
    estimated_duration_seconds FLOAT NOT NULL
);

CREATE TABLE visual_briefs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    production_id uuid NOT NULL REFERENCES productions(id) ON DELETE CASCADE,
    scene_id uuid NOT NULL REFERENCES narrative_blocks(id) ON DELETE CASCADE,
    scene_index INT NOT NULL,
    tema TEXT NOT NULL,
    funcao_visual VARCHAR(50) NOT NULL,
    assunto_visivel TEXT,
    contexto_geografico_cultural TEXT,
    periodo TEXT,
    tom_editorial TEXT,
    nivel_literalidade VARCHAR(20),
    permitidos TEXT[],
    proibidos TEXT[],
    tipo_ativo_preferido VARCHAR(20)
);

CREATE TABLE asset_candidates (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    production_id uuid NOT NULL REFERENCES productions(id) ON DELETE CASCADE,
    scene_id uuid NOT NULL REFERENCES narrative_blocks(id) ON DELETE CASCADE,
    source VARCHAR(50),
    asset_type VARCHAR(20),
    reference TEXT,
    url TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
);

CREATE TABLE verification_scores (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id uuid NOT NULL REFERENCES asset_candidates(id) ON DELETE CASCADE,
    scene_id uuid NOT NULL REFERENCES narrative_blocks(id) ON DELETE CASCADE,
    score FLOAT NOT NULL CHECK (score >= 0 AND score <= 100),
    justification TEXT,
    decision VARCHAR(30) NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE review_queue_items (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    production_id uuid NOT NULL REFERENCES productions(id) ON DELETE CASCADE,
    scene_id uuid NOT NULL REFERENCES narrative_blocks(id) ON DELETE CASCADE,
    asset_id uuid REFERENCES asset_candidates(id),
    score_id uuid REFERENCES verification_scores(id),
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'requeried')),
    reviewed_by uuid REFERENCES users(id),
    reviewed_at timestamptz,
    review_reason TEXT
);

CREATE TABLE manual_bindings (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    production_id uuid NOT NULL REFERENCES productions(id) ON DELETE CASCADE,
    scene_id uuid NOT NULL REFERENCES narrative_blocks(id) ON DELETE CASCADE,
    asset_reference TEXT NOT NULL,
    asset_type VARCHAR(20) NOT NULL,
    bound_by uuid NOT NULL REFERENCES users(id),
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE compositions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    production_id uuid NOT NULL REFERENCES productions(id) ON DELETE CASCADE,
    template_type_id VARCHAR(50) REFERENCES templates(id),
    variation_id VARCHAR(10),
    total_duration_seconds FLOAT,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE composition_slots (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    composition_id uuid NOT NULL REFERENCES compositions(id) ON DELETE CASCADE,
    slot_index INT NOT NULL,
    slot_type VARCHAR(30) NOT NULL,
    duration_seconds FLOAT NOT NULL,
    content_reference TEXT,
    asset_url TEXT,
    manual_binding_id uuid REFERENCES manual_bindings(id)
);

CREATE TABLE render_jobs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    production_id uuid NOT NULL REFERENCES productions(id) ON DELETE CASCADE,
    composition_id uuid REFERENCES compositions(id),
    provider VARCHAR(50) NOT NULL,
    external_job_id VARCHAR,
    status VARCHAR(20) NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'processing', 'completed', 'failed')),
    error_message TEXT,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE render_job_events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    render_job_id uuid NOT NULL REFERENCES render_jobs(id) ON DELETE CASCADE,
    from_status VARCHAR(20),
    to_status VARCHAR(20) NOT NULL,
    reason TEXT,
    occurred_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE audit_events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(50) NOT NULL,
    production_id uuid REFERENCES productions(id),
    user_id uuid REFERENCES users(id),
    timestamp timestamptz NOT NULL DEFAULT now(),
    details JSONB
);

CREATE INDEX idx_productions_organization_id ON productions (organization_id);
CREATE INDEX idx_productions_operator_user_id ON productions (operator_user_id);
CREATE INDEX idx_productions_current_state ON productions (current_state);
CREATE INDEX idx_productions_created_at ON productions (created_at);

CREATE INDEX idx_production_state_transitions_production_id ON production_state_transitions (production_id);
CREATE INDEX idx_production_state_transitions_occurred_at ON production_state_transitions (occurred_at);

CREATE INDEX idx_review_queue_items_production_id ON review_queue_items (production_id);
CREATE INDEX idx_review_queue_items_status ON review_queue_items (status);

CREATE INDEX idx_render_jobs_production_id ON render_jobs (production_id);
CREATE INDEX idx_render_jobs_status ON render_jobs (status);

CREATE INDEX idx_audit_events_event_type ON audit_events (event_type);
CREATE INDEX idx_audit_events_production_id ON audit_events (production_id);
CREATE INDEX idx_audit_events_timestamp ON audit_events (timestamp);

COMMIT;
