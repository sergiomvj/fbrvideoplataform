# Development Funnel — Motor Editorial de Vídeos Templated

> Consolidado a partir de `prd/conceito_geral_article_video.md`, `prd/prd_article_video.md`, `prd/spec_article_video.md`, `prd/interface_ux_article_video.md` e `prd/architecture_article_video.md`  
> Objetivo: transformar o projeto em um backlog executável por múltiplos devs em paralelo, com dependências explícitas e encaixe natural entre módulos

---

## 1. Estratégia do funil

O projeto será executado como um **programa brownfield-greenfield híbrido**, com base documental fechada e implementação incremental em ondas paralelas.

Princípios do funil:

1. nenhum dev começa sem story autocontida
2. toda story define entradas, saídas, dependências e arquivos-alvo
3. o paralelismo deve ocorrer por **fronteira de módulo**, não por “divisão informal de tarefas”
4. integrações entre stories devem acontecer por contratos de domínio, e não por combinações ad hoc entre devs
5. cada onda entrega blocos integráveis e testáveis

---

## 2. Épicos

### Epic 1 — Foundation & Core Platform

Objetivo:

- criar a base operacional segura do sistema
- estabelecer runtime, autenticação, observabilidade e estado central

Stories:

- `1.1` Platform Foundation & Workspace Bootstrap
- `1.2` Auth Session & Secure API Gateway
- `1.3` Core Production Domain & Workflow State Model
- `1.4` Audit Observability & Operational Telemetry

### Epic 2 — Editorial Pipeline Core

Objetivo:

- implementar o núcleo proprietário de estruturação editorial e contratos de template

Stories:

- `2.1` Template Registry, Variation Contracts & Production Intake APIs
- `2.2` Editorial Structuring Engine
- `2.3` Visual Brief Planning Engine

### Epic 3 — Media Intelligence & Review Control

Objetivo:

- implementar sourcing, score contextual, requery, revisão humana e overrides

Stories:

- `3.1` Media Source Adapter Layer
- `3.2` Context Verification Scoring Engine
- `3.3` Requery Loop, Structural Failure Handling & Review Queue Backend
- `3.4` Manual Guided Asset Binding & Override Workflow

### Epic 4 — Composition & Render Execution

Objetivo:

- montar a peça final por template e entregar ao executor externo de render

Stories:

- `4.1` Presenter Short Composition Engine
- `4.2` VideoDoc Composition Engine
- `4.3` Render Lifecycle, HeyGen Adapter & Status Tracking

### Epic 5 — Frontend Operational Console

Objetivo:

- construir a interface operacional que expõe o fluxo com clareza, auditabilidade e eficiência

Stories:

- `5.1` Frontend Shell & Design System Foundation
- `5.2` New Production Wizard
- `5.3` Media Curation & Human Review Workspace
- `5.4` Production Detail, Composition Preview & Render Monitoring

### Epic 6 — Orchestration, Agents & Runtime Ops

Objetivo:

- plugar n8n, OpenClaw, FBR-Click, deploy e monitoramento

Stories:

- `6.1` n8n Orchestration, OpenClaw Assistants & FBR-Click Notifications
- `6.2` Deployment Baseline, Monitoring & Runtime Hardening

---

## 3. Ondas de execução paralela

### Wave 0 — Base operacional

Stories:

- `1.1`
- `1.2`
- `1.4`
- `5.1`
- `6.2`

Resultado esperado:

- workspace e runtime preparados
- autenticação e proxy seguros definidos
- observabilidade mínima disponível
- shell frontend pronto
- baseline de deploy e monitoramento pronta para o restante do projeto

### Wave 1 — Núcleo de domínio

Stories:

- `1.3`
- `2.1`
- `6.1`

Dependências:

- requer `1.1`
- `2.1` consome decisões de `1.3`
- `6.1` depende do baseline de `6.2`

Resultado esperado:

- modelo de produção e estados fechado
- contratos de template e intake definidos
- orquestração de alto nível pronta para ser conectada às próximas etapas

### Wave 2 — Pipeline editorial

Stories:

- `2.2`
- `2.3`
- `3.1`

Dependências:

- `2.2` depende de `1.3` e `2.1`
- `2.3` depende de `2.2`
- `3.1` depende de `2.1`

Resultado esperado:

- estrutura editorial produzida
- briefs visuais gerados
- sourcing de mídia com interface abstrata pronto

### Wave 3 — Controle de mídia

Stories:

- `3.2`
- `3.3`
- `3.4`

Dependências:

- `3.2` depende de `2.3` e `3.1`
- `3.3` depende de `3.2`
- `3.4` depende de `2.1`, `1.3` e `3.3`

Resultado esperado:

- score contextual funcional
- loop de requery implementado
- fila de revisão humana pronta
- fluxo manual guiado e override definidos

### Wave 4 — Montagem e render

Stories:

- `4.1`
- `4.2`
- `4.3`

Dependências:

- `4.1` depende de `2.2`, `2.3`, `3.2`, `3.4`
- `4.2` depende de `2.2`, `2.3`, `3.2`, `3.4`
- `4.3` depende de `4.1` e `4.2`

Resultado esperado:

- composição por template pronta
- integração de render completa
- ciclo de status do render persistido

### Wave 5 — Console operacional completo

Stories:

- `5.2`
- `5.3`
- `5.4`

Dependências:

- `5.2` depende de `5.1`, `2.1`, `2.2`
- `5.3` depende de `5.1`, `3.2`, `3.3`, `3.4`
- `5.4` depende de `5.1`, `4.1`, `4.2`, `4.3`

Resultado esperado:

- operador consegue criar, revisar, acompanhar e disparar produções ponta a ponta

---

## 4. Lanes de trabalho simultâneo

### Lane A — Platform / Infra

Responsável típico:

- `@devops`
- apoio de `@architect`

Stories:

- `1.1`
- `6.2`

### Lane B — Core Backend / Domain

Responsável típico:

- `@dev`
- revisão de `@architect`

Stories:

- `1.2`
- `1.3`
- `1.4`
- `2.1`
- `2.2`
- `2.3`
- `3.1`
- `3.2`
- `3.3`
- `3.4`
- `4.1`
- `4.2`
- `4.3`

### Lane C — Frontend / UX System

Responsável típico:

- `@ux-design-expert`
- implementação por `@dev`

Stories:

- `5.1`
- `5.2`
- `5.3`
- `5.4`

### Lane D — Orchestration / Agentic Ops

Responsável típico:

- `@architect`
- implementação por `@dev` ou `@devops` conforme submódulo

Stories:

- `6.1`

---

## 5. Regras de encaixe entre devs paralelos

1. **Nenhuma story modifica contrato de outra story sem explicitar isso em Cross-Story Decisions.**
2. **Todo módulo expõe saídas versionáveis e previsíveis.**
3. **Dev Notes de cada story devem ser suficientes para o executor não depender de leitura difusa da documentação-mãe.**
4. **Stories de UI só consomem APIs e estados previamente definidos nas stories de backend.**
5. **Stories de composição não devem redefinir regras de sourcing ou score.**
6. **Stories de revisão humana não podem reabrir contratos de template já fechados em Epic 2.**

---

## 6. Ordem recomendada de aprovação para execução

1. aprovar todas as stories de Epic 1
2. aprovar Epic 2 e Epic 6.1
3. aprovar Epic 3
4. aprovar Epic 4
5. aprovar Epic 5

Isso permite iniciar implementação com mínima ambiguidade e máximo paralelismo útil.

---

## 7. Checklist de readiness do backlog

- [ ] Todas as stories existem em `docs/stories/`
- [ ] Todas as stories têm dependências explícitas
- [ ] Todas as stories têm executor e quality gate definidos
- [ ] Todas as stories incluem critérios de aceite verificáveis
- [ ] Todas as stories indicam arquivos-alvo esperados
- [ ] O backlog cobre todos os módulos definidos na arquitetura
- [ ] O backlog cobre todos os fluxos definidos no PRD/SPEC

