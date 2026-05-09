# Help Completo de Funcionalidades

## 1. Visao geral

O projeto `1FBRFaceVideo` implementa um motor editorial de producao de videos templated com dois templates principais:

- `presenter_short`
- `videodoc_narrated`

O sistema esta dividido em:

- frontend operacional em `Next.js`
- backend de dominio e APIs em `FastAPI`
- integracoes com render externo, sourcing de midia, observabilidade e notificacoes

## 2. Funcionalidades atualmente expostas

### 2.1 Frontend

Rotas atualmente presentes em `frontend/app`:

- `/`
  - tela inicial simples com mensagem de boas-vindas
- `/productions/new`
  - wizard de criacao de producao
- `/productions/[id]`
  - detalhe de producao, timeline, preview e status de render
- `/review`
  - fila de revisao humana
- `/api/auth/session`
  - sessao local com `iron-session`
- `/api/[...path]`
  - gateway autenticado para o backend

### 2.2 Backend

Rotas FastAPI atualmente registradas:

- `GET /health`
  - health check da API
- `GET /metrics`
  - metricas Prometheus
- `GET /productions/`
  - lista producoes do usuario autenticado
- `POST /productions/`
  - cria uma nova producao
- `GET /productions/{production_id}`
  - busca uma producao
- `POST /productions/{production_id}/structure`
  - roda estruturacao editorial
- `POST /productions/{production_id}/plan-visual`
  - gera briefs visuais
- `POST /productions/{production_id}/events`
  - emite eventos manuais de dominio
- `GET /templates/`
  - lista templates
- `GET /templates/{template_type_id}`
  - detalhe de template
- `POST /media-sourcing/source`
  - busca candidatos de midia
- `POST /media-sourcing/asset`
  - resolve asset por fonte externa
- `GET /review/{production_id}`
  - lista itens pendentes de revisao
- `POST /review/{production_id}/{item_id}/approve`
  - aprova item de revisao
- `POST /review/{production_id}/{item_id}/reject`
  - rejeita item de revisao
- `POST /renders/{production_id}/submit`
  - submete render
- `GET /renders/{production_id}/status`
  - consulta status de render

## 3. Fluxos funcionais

### 3.1 Criacao de producao

Tela:

- `frontend/app/productions/new/page.tsx`

Passos atuais do wizard:

1. selecionar modo
2. selecionar template
3. selecionar variacao
4. preencher conteudo

Campos atuais:

- `title`
- `base_content`
- `editorial_context`
- `restrictions`
- `mode`
- `template_type_id`
- `variation_id`

Resultado:

- cria a producao no backend
- redireciona via link para a tela de detalhe

### 3.2 Estruturacao editorial

Servico principal:

- `backend/application/services/structuring/engine.py`

Objetivo:

- transformar a entrada em uma narrativa estruturada
- respeitar restricoes do template
- produzir blocos narrativos com duracao estimada

### 3.3 Planejamento visual

Servico principal:

- `backend/application/services/visual_planning/engine.py`

Objetivo:

- converter blocos narrativos em briefs visuais por cena
- definir tema, funcao visual, assunto visivel, contexto, proibidos e tipo de ativo

### 3.4 Sourcing de midia

Servico principal:

- `backend/application/services/media_sourcing/`

Integracoes registradas no startup:

- `stock_media_adapter`
- `archive_media_adapter`

Objetivo:

- buscar candidatos de midia por brief visual
- devolver ativos com metadados basicos

### 3.5 Verificacao contextual

Modulo principal:

- `backend/domain/context_verification/`

Objetivo:

- calcular score de aderencia contextual
- registrar justificativas
- suportar decisao automatica, revisao humana ou requery

### 3.6 Revisao humana

Modulo principal:

- `backend/domain/human_review/`

Objetivo:

- manter fila de revisao
- aprovar ou rejeitar candidatos
- permitir bindings manuais

### 3.7 Bindings manuais

Servico principal:

- `backend/application/services/manual_binding/service.py`

Objetivo:

- permitir vincular um asset manualmente a uma cena
- definir preferencia, obrigatoriedade, proibicao ou fixacao
- sobrescrever decisao automatica na composicao

### 3.8 Composicao

Modulos principais:

- `backend/domain/composition/presenter_short/`
- `backend/domain/composition/videodoc/`

Objetivo:

- montar timelines por template
- combinar narrativa, midia e bindings manuais
- preparar a composicao para o adapter de render

### 3.9 Render

Integracao principal:

- `backend/integrations/heygen/adapter.py`

Objetivo:

- converter composicao em payload do provedor
- criar job de render
- consultar ciclo de vida do job

### 3.10 Observabilidade

Pontos expostos:

- `GET /health`
- `GET /metrics`

Artefatos relacionados:

- `docs/telemetry-usage-guide.md`
- `infra/` com baseline operacional

## 4. Templates suportados

### 4.1 Presenter Short

Caracteristicas conceituais:

- foco em video curto
- avatar ou apresentador
- variacoes controladas
- composicao enxuta

### 4.2 VideoDoc Narrated

Caracteristicas conceituais:

- fluxo mais longo
- narrativa com apoio de imagem e video
- slots de b-roll e apoio visual

## 5. Modos de operacao

### 5.1 Automatico

Objetivo:

- receber conteudo base
- gerar estrutura narrativa
- gerar briefs visuais
- buscar midia
- decidir por score
- compor e renderizar

### 5.2 Manual

Objetivo:

- permitir controle maior do operador
- usar bindings e overrides
- preservar estrutura do template com maior intervencao humana

## 6. Estado e workflow

Modelo principal:

- `backend/domain/production/aggregate.py`

Responsabilidades:

- manter estado atual da producao
- registrar historico de transicoes
- impedir saltos invalidos no workflow

## 7. Seguranca e autenticacao

Camadas atuais:

- sessao frontend com `iron-session`
- gateway frontend para backend
- autenticacao backend por header `X-User-Id`

Arquivos principais:

- `frontend/app/api/auth/session/route.ts`
- `frontend/lib/session/index.ts`
- `frontend/lib/gateway/index.ts`
- `backend/application/security/auth.py`

## 8. Documentacao existente no projeto

Base de produto e arquitetura:

- `prd/conceito_geral_article_video.md`
- `prd/prd_article_video.md`
- `prd/spec_article_video.md`
- `prd/interface_ux_article_video.md`
- `prd/architecture_article_video.md`

Documentacao complementar:

- `docs/development-funnel-article-video.md`
- `docs/auth-gateway-pattern.md`
- `docs/production-workflow-model.md`
- `docs/template-registry-and-intake-contract.md`
- `docs/telemetry-usage-guide.md`

Stories:

- `docs/stories/`

## 9. Limitacoes atuais observadas

Este help descreve o que o codigo implementa hoje, mas algumas partes ainda estao em maturacao ou revisao. Exemplos:

- parte do estado operacional esta em memoria
- algumas telas frontend ainda dependem de alinhamento fino com os contratos do backend
- a experiencia manual guiada ainda nao cobre toda a fase pre-fluxo descrita nos documentos de produto
- a documentacao de onboarding tecnico ainda esta incompleta

## 10. Como validar rapidamente o sistema

### Frontend

No diretorio `frontend`:

```bash
npm run lint
npm run build
```

### Backend

No diretorio `backend`:

```bash
python -m pytest
```

Observacao:

- o ambiente local precisa ter `pytest` instalado para a execucao dos testes do backend

## 11. Uso recomendado deste help

Este documento deve ser usado como referencia de:

- onboarding de devs
- auditoria de cobertura funcional
- alinhamento entre frontend, backend e stories
- base para um futuro manual do operador
