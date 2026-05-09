# Database Model — Motor Editorial de Vídeos Templated

> Baseado em `conceito_geral_article_video.md`, `prd_article_video.md`, `spec_article_video.md`, `architecture_article_video.md` e nos findings da auditoria técnica  
> Objetivo: modelar o banco transacional necessário para sustentar o sistema com histórico completo de operações, auditabilidade, rastreabilidade por cena e persistência real do workflow

---

## 1. Objetivos do modelo

O banco precisa sustentar:

1. persistência transacional das produções
2. histórico completo de estados e decisões
3. rastreabilidade entre conteúdo, cena, mídia, score, revisão humana, composição e render
4. isolamento por organização e operador
5. auditabilidade completa de ações humanas e automáticas
6. suporte a retries, requery, overrides manuais e integrações externas

---

## 2. Princípios de modelagem

1. **PostgreSQL 16** como banco transacional principal
2. **Current state + append-only history**
3. **Toda entidade operacional importante tem `id`, `created_at`, `updated_at`**
4. **Soft delete apenas onde fizer sentido operacional**
5. **Toda ação relevante gera evento auditável**
6. **Toda decisão automática relevante é explicável e persistida**
7. **Relacionamentos fortes por foreign keys**
8. **JSONB apenas para payload variável, nunca para esconder domínio principal**

---

## 3. Estratégia de histórico completo

Para manter histórico completo sem tornar o sistema impraticável, o modelo usa duas camadas:

### 3.1 Tabelas de estado atual

Guardam o retrato vigente da operação.

Exemplos:

- `productions`
- `review_queue_items`
- `render_jobs`
- `manual_asset_bindings`

### 3.2 Tabelas históricas append-only

Guardam tudo o que aconteceu ao longo do fluxo.

Exemplos:

- `production_state_transitions`
- `asset_score_breakdowns`
- `asset_decision_events`
- `review_actions`
- `render_job_events`
- `audit_events`
- `integration_request_logs`

Essa combinação atende bem:

- consultas operacionais rápidas no presente
- reconstrução histórica completa quando necessário

---

## 4. Domínios de dados

O banco será organizado em sete domínios:

1. identidade e tenancy
2. templates e configuração
3. produção editorial
4. mídia e verificação contextual
5. revisão humana e override manual
6. composição e render
7. auditoria e observabilidade operacional

---

## 5. Entidades principais

## 5.1 Identidade e tenancy

### `users`

Representa operadores humanos autenticados.

Campos principais:

- `id uuid pk`
- `email text unique not null`
- `display_name text not null`
- `status text not null`
- `created_at timestamptz not null`
- `updated_at timestamptz not null`

### `organizations`

Representa empresa/redação cliente ou unidade operacional.

Campos principais:

- `id uuid pk`
- `name text not null`
- `slug text unique not null`
- `status text not null`
- `created_at timestamptz not null`
- `updated_at timestamptz not null`

### `organization_memberships`

Relaciona usuário e organização com papel.

Campos principais:

- `id uuid pk`
- `organization_id uuid fk -> organizations.id`
- `user_id uuid fk -> users.id`
- `role text not null`
- `status text not null`
- `created_at timestamptz not null`
- `updated_at timestamptz not null`

Índices:

- unique (`organization_id`, `user_id`)

---

## 5.2 Templates e configuração

### `template_types`

Registra templates suportados.

Campos principais:

- `id uuid pk`
- `type_key text unique not null`
- `name text not null`
- `description text`
- `aspect_ratio text not null`
- `resolution text not null`
- `max_duration_seconds integer not null`
- `min_scenes integer not null`
- `max_scenes integer not null`
- `supports_broll boolean not null`
- `status text not null`
- `created_at timestamptz not null`
- `updated_at timestamptz not null`

### `template_variations`

Registra as variações `1`, `2`, `3` por template.

Campos principais:

- `id uuid pk`
- `template_type_id uuid fk -> template_types.id`
- `variation_key text not null`
- `label text not null`
- `description text`
- `status text not null`
- `created_at timestamptz not null`
- `updated_at timestamptz not null`

Índices:

- unique (`template_type_id`, `variation_key`)

### `organization_template_profiles`

Permite customização por organização.

Campos principais:

- `id uuid pk`
- `organization_id uuid fk -> organizations.id`
- `template_type_id uuid fk -> template_types.id`
- `default_variation_id uuid fk -> template_variations.id`
- `default_avatar_ref text`
- `default_background_ref text`
- `editorial_style jsonb not null default '{}'::jsonb`
- `restrictions jsonb not null default '{}'::jsonb`
- `created_at timestamptz not null`
- `updated_at timestamptz not null`

---

## 5.3 Produção editorial

### `productions`

Entidade raiz da operação.

Campos principais:

- `id uuid pk`
- `organization_id uuid fk -> organizations.id`
- `operator_user_id uuid fk -> users.id`
- `mode text not null`
- `current_state text not null`
- `template_type_id uuid fk -> template_types.id`
- `template_variation_id uuid fk -> template_variations.id`
- `title text not null`
- `base_content text`
- `editorial_context text`
- `restrictions text`
- `source_type text`
- `priority text not null default 'normal'`
- `created_at timestamptz not null`
- `updated_at timestamptz not null`
- `deleted_at timestamptz null`

Índices:

- (`organization_id`, `created_at desc`)
- (`operator_user_id`, `created_at desc`)
- (`current_state`)

### `production_inputs`

Snapshot normalizado da entrada recebida.

Campos principais:

- `id uuid pk`
- `production_id uuid fk -> productions.id`
- `input_type text not null`
- `input_payload jsonb not null`
- `submitted_by_user_id uuid fk -> users.id`
- `created_at timestamptz not null`

Observação:

Cada ressubmissão ou alteração estrutural pode gerar novo registro sem apagar o anterior.

### `production_state_transitions`

Histórico completo do workflow.

Campos principais:

- `id uuid pk`
- `production_id uuid fk -> productions.id`
- `from_state text`
- `to_state text not null`
- `reason text`
- `triggered_by_type text not null`
- `triggered_by_user_id uuid fk -> users.id null`
- `triggered_by_system text null`
- `trace_id uuid null`
- `occurred_at timestamptz not null`

Índices:

- (`production_id`, `occurred_at`)

### `production_failures`

Falhas estruturais ou operacionais relevantes.

Campos principais:

- `id uuid pk`
- `production_id uuid fk -> productions.id`
- `failure_type text not null`
- `stage text not null`
- `message text not null`
- `details jsonb not null default '{}'::jsonb`
- `created_at timestamptz not null`

---

## 5.4 Estrutura narrativa

### `narrative_structures`

Representa uma versão estruturada da narrativa.

Campos principais:

- `id uuid pk`
- `production_id uuid fk -> productions.id`
- `version integer not null`
- `objective text`
- `target_duration_seconds integer`
- `total_duration_seconds integer`
- `status text not null`
- `generated_by_type text not null`
- `generated_by_user_id uuid fk -> users.id null`
- `generated_by_system text null`
- `created_at timestamptz not null`

Índices:

- unique (`production_id`, `version`)

### `narrative_blocks`

Blocos ou cenas da narrativa.

Campos principais:

- `id uuid pk`
- `narrative_structure_id uuid fk -> narrative_structures.id`
- `scene_index integer not null`
- `narrative_role text not null`
- `text_content text not null`
- `estimated_duration_seconds integer not null`
- `metadata jsonb not null default '{}'::jsonb`
- `created_at timestamptz not null`
- `updated_at timestamptz not null`

Índices:

- (`narrative_structure_id`, `scene_index`)

---

## 5.5 Brief visual e sourcing de mídia

### `scene_visual_briefs`

Brief visual por cena.

Campos principais:

- `id uuid pk`
- `production_id uuid fk -> productions.id`
- `narrative_block_id uuid fk -> narrative_blocks.id`
- `version integer not null`
- `theme text not null`
- `visual_function text not null`
- `visible_subject text not null`
- `geo_cultural_context text`
- `time_period text`
- `editorial_tone text`
- `literalness_level text not null`
- `allowed_elements jsonb not null default '[]'::jsonb`
- `forbidden_elements jsonb not null default '[]'::jsonb`
- `preferred_asset_type text not null`
- `created_at timestamptz not null`

Índices:

- (`production_id`, `narrative_block_id`)

### `media_sources`

Catálogo de fontes de mídia.

Campos principais:

- `id uuid pk`
- `source_key text unique not null`
- `name text not null`
- `source_type text not null`
- `status text not null`
- `config jsonb not null default '{}'::jsonb`
- `created_at timestamptz not null`
- `updated_at timestamptz not null`

### `media_query_attempts`

Histórico de tentativas automáticas de obtenção.

Campos principais:

- `id uuid pk`
- `production_id uuid fk -> productions.id`
- `scene_visual_brief_id uuid fk -> scene_visual_briefs.id`
- `attempt_number integer not null`
- `source_id uuid fk -> media_sources.id`
- `query_strategy text not null`
- `query_payload jsonb not null`
- `diagnostic_reason text null`
- `triggered_by text not null`
- `started_at timestamptz not null`
- `finished_at timestamptz null`
- `status text not null`

Índices:

- (`production_id`, `scene_visual_brief_id`, `attempt_number`)

### `asset_candidates`

Cada ativo retornado por uma tentativa de sourcing.

Campos principais:

- `id uuid pk`
- `production_id uuid fk -> productions.id`
- `scene_visual_brief_id uuid fk -> scene_visual_briefs.id`
- `query_attempt_id uuid fk -> media_query_attempts.id`
- `source_id uuid fk -> media_sources.id`
- `external_asset_id text not null`
- `media_type text not null`
- `asset_url text not null`
- `thumbnail_url text`
- `title text`
- `description text`
- `metadata jsonb not null default '{}'::jsonb`
- `created_at timestamptz not null`

Índices:

- (`production_id`, `scene_visual_brief_id`)
- (`source_id`, `external_asset_id`)

---

## 5.6 Score contextual e decisão operacional

### `asset_score_runs`

Cada execução do mecanismo de scoring.

Campos principais:

- `id uuid pk`
- `production_id uuid fk -> productions.id`
- `asset_candidate_id uuid fk -> asset_candidates.id`
- `scene_visual_brief_id uuid fk -> scene_visual_briefs.id`
- `scoring_model text not null`
- `scoring_version text not null`
- `final_score numeric(5,2) not null`
- `decision_band text not null`
- `short_justification text`
- `conflict_flags jsonb not null default '[]'::jsonb`
- `created_at timestamptz not null`

Índices:

- (`production_id`, `asset_candidate_id`)

### `asset_score_breakdowns`

Persistência detalhada dos critérios que compõem o score.

Campos principais:

- `id uuid pk`
- `asset_score_run_id uuid fk -> asset_score_runs.id`
- `criterion_key text not null`
- `weight numeric(5,2) not null`
- `score numeric(5,2) not null`
- `explanation text`
- `created_at timestamptz not null`

Índices:

- (`asset_score_run_id`, `criterion_key`)

### `asset_decisions`

Estado operacional vigente de cada candidato ou cena.

Campos principais:

- `id uuid pk`
- `production_id uuid fk -> productions.id`
- `scene_visual_brief_id uuid fk -> scene_visual_briefs.id`
- `asset_candidate_id uuid fk -> asset_candidates.id`
- `asset_score_run_id uuid fk -> asset_score_runs.id`
- `decision_status text not null`
- `decision_origin text not null`
- `is_current boolean not null default true`
- `decided_by_user_id uuid fk -> users.id null`
- `decided_by_system text null`
- `decided_at timestamptz not null`

Índices:

- partial unique on (`scene_visual_brief_id`) where `is_current = true` and `decision_status in ('auto_approved','human_approved','manual_fixed')`

### `asset_decision_events`

Histórico append-only de todas as decisões e mudanças.

Campos principais:

- `id uuid pk`
- `asset_decision_id uuid fk -> asset_decisions.id`
- `previous_status text`
- `new_status text not null`
- `reason text`
- `actor_type text not null`
- `actor_user_id uuid fk -> users.id null`
- `actor_system text null`
- `created_at timestamptz not null`

---

## 5.7 Revisão humana e override manual

### `review_queue_items`

Item de fila vigente.

Campos principais:

- `id uuid pk`
- `production_id uuid fk -> productions.id`
- `scene_visual_brief_id uuid fk -> scene_visual_briefs.id`
- `asset_candidate_id uuid fk -> asset_candidates.id`
- `asset_score_run_id uuid fk -> asset_score_runs.id`
- `status text not null`
- `priority text not null default 'normal'`
- `assigned_to_user_id uuid fk -> users.id null`
- `enqueued_at timestamptz not null`
- `resolved_at timestamptz null`
- `created_at timestamptz not null`
- `updated_at timestamptz not null`

Índices:

- (`status`, `priority`, `enqueued_at`)
- (`production_id`, `status`)

### `review_actions`

Histórico de ações humanas na revisão.

Campos principais:

- `id uuid pk`
- `review_queue_item_id uuid fk -> review_queue_items.id`
- `action_type text not null`
- `performed_by_user_id uuid fk -> users.id`
- `comment text`
- `payload jsonb not null default '{}'::jsonb`
- `created_at timestamptz not null`

### `manual_asset_bindings`

Binding manual vigente ou histórico lógico.

Campos principais:

- `id uuid pk`
- `production_id uuid fk -> productions.id`
- `scene_visual_brief_id uuid fk -> scene_visual_briefs.id`
- `narrative_block_id uuid fk -> narrative_blocks.id null`
- `asset_candidate_id uuid fk -> asset_candidates.id null`
- `binding_type text not null`
- `asset_url text not null`
- `asset_title text`
- `status text not null`
- `bound_by_user_id uuid fk -> users.id not null`
- `template_type_id uuid fk -> template_types.id null`
- `metadata jsonb not null default '{}'::jsonb`
- `created_at timestamptz not null`
- `updated_at timestamptz not null`

Índices:

- (`production_id`, `scene_visual_brief_id`, `status`)

### `manual_binding_events`

Histórico append-only de criação, remoção e override de bindings.

Campos principais:

- `id uuid pk`
- `manual_asset_binding_id uuid fk -> manual_asset_bindings.id`
- `event_type text not null`
- `actor_user_id uuid fk -> users.id`
- `details jsonb not null default '{}'::jsonb`
- `created_at timestamptz not null`

---

## 5.8 Composição e render

### `production_compositions`

Representa uma composição final ou intermediária.

Campos principais:

- `id uuid pk`
- `production_id uuid fk -> productions.id`
- `template_type_id uuid fk -> template_types.id`
- `template_variation_id uuid fk -> template_variations.id`
- `version integer not null`
- `status text not null`
- `narration_text text`
- `timeline_payload jsonb not null`
- `metadata jsonb not null default '{}'::jsonb`
- `created_at timestamptz not null`
- `updated_at timestamptz not null`

Índices:

- unique (`production_id`, `version`)

### `composition_slots`

Slots renderizáveis da composição.

Campos principais:

- `id uuid pk`
- `composition_id uuid fk -> production_compositions.id`
- `slot_index integer not null`
- `slot_type text not null`
- `duration_seconds integer not null`
- `content_ref text`
- `scene_visual_brief_id uuid fk -> scene_visual_briefs.id null`
- `asset_candidate_id uuid fk -> asset_candidates.id null`
- `manual_asset_binding_id uuid fk -> manual_asset_bindings.id null`
- `payload jsonb not null default '{}'::jsonb`
- `created_at timestamptz not null`

Índices:

- (`composition_id`, `slot_index`)

### `render_jobs`

Job de render atual por submissão.

Campos principais:

- `id uuid pk`
- `production_id uuid fk -> productions.id`
- `composition_id uuid fk -> production_compositions.id`
- `provider_key text not null`
- `external_job_id text null`
- `status text not null`
- `submitted_by_type text not null`
- `submitted_by_user_id uuid fk -> users.id null`
- `progress_percent numeric(5,2) null`
- `output_url text null`
- `error_message text null`
- `created_at timestamptz not null`
- `updated_at timestamptz not null`

Índices:

- (`production_id`, `created_at desc`)
- (`provider_key`, `external_job_id`)

### `render_job_events`

Histórico append-only do ciclo de vida do render.

Campos principais:

- `id uuid pk`
- `render_job_id uuid fk -> render_jobs.id`
- `previous_status text`
- `new_status text not null`
- `provider_payload jsonb not null default '{}'::jsonb`
- `error_message text null`
- `created_at timestamptz not null`

---

## 5.9 Auditoria e observabilidade

### `domain_events`

Registro funcional de eventos de domínio emitidos.

Campos principais:

- `id uuid pk`
- `event_type text not null`
- `production_id uuid fk -> productions.id null`
- `entity_type text not null`
- `entity_id uuid null`
- `payload jsonb not null`
- `source text not null`
- `trace_id uuid null`
- `created_at timestamptz not null`

Índices:

- (`production_id`, `created_at`)
- (`event_type`, `created_at`)

### `audit_events`

Log estruturado de auditoria orientado a compliance e rastreabilidade.

Campos principais:

- `id uuid pk`
- `organization_id uuid fk -> organizations.id null`
- `production_id uuid fk -> productions.id null`
- `entity_type text not null`
- `entity_id text not null`
- `event_type text not null`
- `actor_type text not null`
- `actor_user_id uuid fk -> users.id null`
- `before_state jsonb null`
- `after_state jsonb null`
- `metadata jsonb not null default '{}'::jsonb`
- `trace_id uuid null`
- `created_at timestamptz not null`

Índices:

- (`production_id`, `created_at desc`)
- (`actor_user_id`, `created_at desc`)
- (`entity_type`, `entity_id`, `created_at desc`)

### `integration_request_logs`

Histórico de chamadas a integrações externas.

Campos principais:

- `id uuid pk`
- `production_id uuid fk -> productions.id null`
- `integration_key text not null`
- `operation_key text not null`
- `request_payload jsonb not null`
- `response_payload jsonb null`
- `http_status integer null`
- `status text not null`
- `started_at timestamptz not null`
- `finished_at timestamptz null`
- `trace_id uuid null`

Índices:

- (`integration_key`, `started_at desc`)
- (`production_id`, `started_at desc`)

### `llm_execution_logs`

Histórico de chamadas a modelos usados em estruturação, brief e requery.

Campos principais:

- `id uuid pk`
- `production_id uuid fk -> productions.id null`
- `purpose text not null`
- `provider text not null`
- `model text not null`
- `input_hash text not null`
- `input_payload jsonb not null`
- `output_payload jsonb null`
- `status text not null`
- `latency_ms integer null`
- `token_usage jsonb not null default '{}'::jsonb`
- `created_at timestamptz not null`

---

## 6. Relacionamentos essenciais

### Produção

`organizations -> productions -> narrative_structures -> narrative_blocks`

### Planejamento visual

`narrative_blocks -> scene_visual_briefs -> media_query_attempts -> asset_candidates`

### Decisão contextual

`asset_candidates -> asset_score_runs -> asset_score_breakdowns -> asset_decisions`

### Revisão humana

`asset_decisions -> review_queue_items -> review_actions`

### Override manual

`scene_visual_briefs -> manual_asset_bindings -> manual_binding_events`

### Montagem

`productions -> production_compositions -> composition_slots`

### Render

`production_compositions -> render_jobs -> render_job_events`

### Auditoria

Tudo converge em:

- `domain_events`
- `audit_events`
- `integration_request_logs`
- `llm_execution_logs`

---

## 7. Estratégia de integridade

## 7.1 Foreign keys obrigatórias

Todos os relacionamentos centrais devem usar FK real.

## 7.2 Constraints recomendadas

- `productions.mode in ('automatic','manual')`
- `render_jobs.status in ('queued','processing','completed','failed','cancelled')`
- `review_queue_items.status in ('pending','approved','rejected','requery_requested','resolved')`
- `asset_decisions.decision_status in ('auto_approved','human_review_required','rejected_requery','failed_structural','human_approved','human_rejected','manual_fixed')`
- `manual_asset_bindings.binding_type in ('required','fixed','prohibited','preferred')`

## 7.3 Regras de unicidade úteis

- uma produção tem um estado atual único
- uma composição tem versão única por produção
- uma transição histórica nunca é sobrescrita
- uma tentativa de sourcing é numerada por cena

---

## 8. Índices prioritários

### Operação diária

- `productions (organization_id, current_state, created_at desc)`
- `review_queue_items (status, priority, enqueued_at)`
- `render_jobs (production_id, created_at desc)`

### Auditoria e rastreabilidade

- `audit_events (production_id, created_at desc)`
- `domain_events (event_type, created_at desc)`
- `asset_decisions (scene_visual_brief_id, decided_at desc)`

### Reconstrução de contexto

- `narrative_blocks (narrative_structure_id, scene_index)`
- `scene_visual_briefs (production_id, narrative_block_id)`
- `asset_candidates (scene_visual_brief_id, created_at desc)`
- `asset_score_runs (asset_candidate_id, created_at desc)`

---

## 9. Estratégia de multi-tenant

O tenancy inicial deve ser por `organization_id`.

Toda entidade operacional relevante deve carregar:

- `organization_id` diretamente
- ou ter caminho determinístico até `organization_id`

Recomendação prática:

- tabelas raiz carregam `organization_id`
- tabelas derivadas podem inferir por FK, mas views operacionais podem materializar o campo se necessário

Se a implementação final usar RLS:

- políticas por `organization_id`
- eventual filtro complementar por `operator_user_id` onde fizer sentido

---

## 10. Estratégia de evolução

### Fase 1 - Persistência do núcleo

Implementar primeiro:

- `users`
- `organizations`
- `organization_memberships`
- `template_types`
- `template_variations`
- `productions`
- `production_inputs`
- `production_state_transitions`
- `narrative_structures`
- `narrative_blocks`

### Fase 2 - Curadoria e score

- `scene_visual_briefs`
- `media_sources`
- `media_query_attempts`
- `asset_candidates`
- `asset_score_runs`
- `asset_score_breakdowns`
- `asset_decisions`
- `review_queue_items`
- `review_actions`

### Fase 3 - Manual, composição e render

- `manual_asset_bindings`
- `manual_binding_events`
- `production_compositions`
- `composition_slots`
- `render_jobs`
- `render_job_events`

### Fase 4 - Auditoria aprofundada

- `domain_events`
- `audit_events`
- `integration_request_logs`
- `llm_execution_logs`

---

## 11. Observações finais do modelo

Este modelo foi desenhado para resolver os principais gaps atuais do sistema:

- stores em memória
- ausência de histórico robusto
- impossibilidade de auditar decisões automáticas
- falta de persistência do ciclo de render
- falta de suporte real ao fluxo manual guiado

Ele preserva uma arquitetura relacional clara e forte o suficiente para:

- operação diária
- debugging
- revisão humana
- analytics futura
- compliance editorial

O próximo artefato natural a partir deste documento é:

1. `schema.sql` inicial
2. plano de migração por fases
3. mapeamento ORM/repositorios
4. políticas de autorização e, se adotado, RLS
