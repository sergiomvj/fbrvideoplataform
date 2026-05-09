# Store-to-Postgres Migration Plan

## 1. Objetivo

Migrar o sistema de stores em memória para persistência real em PostgreSQL sem quebrar o fluxo atual de desenvolvimento e sem introduzir uma troca abrupta de runtime.

## 2. Stores voláteis identificados

### `backend/api/routes/productions.py`

- `_productions_store`

Impacto:

- perda total de produções em restart
- quebra de rastreabilidade e histórico

### `backend/api/routes/renders.py`

- `_composition_store`

Impacto:

- render depende de composição efêmera
- tela de detalhe não tem base persistida para preview

### `backend/domain/render/models.py`

- `RenderJobStore`

Impacto:

- jobs de render desaparecem em restart
- polling e auditoria ficam incompletos

### Estado correlato de review/scoring

Parte do fluxo de review e decisão também ainda depende de representação transitória em memória e precisa ser persistida de forma completa antes de ser tratada como confiável.

## 3. Estratégia geral

### Princípio

Não substituir tudo de uma vez.

### Método

1. introduzir schema primeiro
2. introduzir repositórios e projeções persistidas
3. migrar runtime por domínio
4. remover store em memória somente depois de verificação

## 4. Fases

## Fase 0 - Preparação

Objetivo:

- estabelecer a base do banco e da camada de acesso

Entregas:

- `infra/postgres/001_initial_schema.sql`
- config de conexão
- pasta/repositórios de infraestrutura de banco
- convenção de transações e IDs

Gate:

- schema validado
- ordem de criação consistente
- ambiente local sobe com PostgreSQL operacional

Rollback:

- nenhuma mudança de runtime ainda

---

## Fase 1 - Persistência do núcleo de produção

Objetivo:

- substituir `_productions_store`

Entregas:

- persistência de `productions`
- persistência de `production_inputs`
- persistência de `production_state_transitions`
- recuperação do aggregate por banco

Estratégia de coexistência:

- manter domínio atual
- substituir apenas a fonte de armazenamento
- rotas continuam com contrato externo equivalente

Gate:

- criar/listar/buscar produção via banco
- transições de estado sobrevivem a restart
- testes de regressão do fluxo `create -> structure -> plan-visual`

Rollback:

- feature flag ou branch de repository adapter para retornar temporariamente ao store em memória enquanto a Fase 1 estiver em estabilização

---

## Fase 2 - Persistência de scoring, decisão e review

Objetivo:

- tornar a cadeia de curadoria totalmente persistida

Entregas:

- `scene_visual_briefs`
- `media_query_attempts`
- `asset_candidates`
- `asset_score_runs`
- `asset_score_breakdowns`
- `asset_decisions`
- `review_queue_items`
- `review_actions`

Estratégia de coexistência:

- primeiro persistir gravação dos artefatos
- depois adaptar rotas `/review`
- por fim alinhar a UI ao payload persistido

Gate:

- uma cena pode ser rastreada do brief até a decisão
- review queue funciona após restart
- approve/reject/requery deixam histórico completo

Rollback:

- manter projeções temporárias de leitura enquanto novos writes são verificados

---

## Fase 3 - Persistência de composição e render

Objetivo:

- substituir `_composition_store` e `RenderJobStore`

Entregas:

- `production_compositions`
- `composition_slots`
- `render_jobs`
- `render_job_events`

Estratégia de coexistência:

- gravar composição persistida antes de submeter render
- adaptar `submit_render` para ler composição persistida
- adaptar `status` para ler job persistido

Gate:

- render job continua consultável após restart
- tela de detalhe exibe preview e status a partir do banco
- eventos de render ficam historizados

Rollback:

- fallback temporário para não submeter render sem composição persistida válida

---

## Fase 4 - Manual guided flow persistido

Objetivo:

- fechar a persistência do modo manual

Entregas:

- `manual_asset_bindings`
- `manual_binding_events`
- APIs de binding
- integração da composição com bindings persistidos

Gate:

- operador cria binding manual
- binding aparece na composição
- override fica auditável

Rollback:

- desabilitar manual mode expandido se os bindings persistidos falharem em validação

---

## Fase 5 - Auditoria e observabilidade aprofundadas

Objetivo:

- consolidar trilha histórica operacional

Entregas:

- `domain_events`
- `audit_events`
- `integration_request_logs`
- `llm_execution_logs`

Gate:

- eventos críticos de produção, review e render ficam consultáveis
- integrações externas podem ser auditadas

Rollback:

- logs estruturados continuam como fallback observável, sem bloquear operação

## 5. Ordem recomendada de execução

1. `7.9` Initial PostgreSQL Schema Bootstrap
2. `7.4` Core Production Persistence
3. `7.5` Review, Composition & Render Persistence
4. `7.2` Review Queue Contract Reconciliation
5. `7.3` Production Detail Contract Reconciliation
6. `7.6` Manual Guided Flow Completion
7. `7.8` Documentation & Operator Help Alignment

## 6. Compatibilidade durante transição

### Regras

1. Não quebrar contratos HTTP externos sem alinhar frontend correspondente.
2. Não remover store em memória antes de validar o repository persistido do mesmo domínio.
3. Cada fase deve ter smoke tests próprios.
4. Toda mudança deve preservar `current state` e `history`.

### Recomendação técnica

Usar adapters/repositories por domínio:

- `ProductionRepository`
- `ReviewRepository`
- `CompositionRepository`
- `RenderJobRepository`

Isso facilita:

- coexistência temporária
- substituição controlada
- testes por implementação

## 7. Checkpoints de verificação

### Checkpoint A - Após Fase 1

- produção criada por API persiste
- listagem por operador funciona
- histórico de transição é reconstruível

### Checkpoint B - Após Fase 2

- review queue não some em restart
- score e justificativa podem ser consultados
- decisões humanas ficam persistidas

### Checkpoint C - Após Fase 3

- render continua operando
- tela de detalhe consegue mostrar composição e render status reais
- job lifecycle completo fica disponível

### Checkpoint D - Após Fase 4

- manual mode deixa de depender de memória ou payload efêmero

## 8. Riscos principais

### Risco 1

Misturar refatoração de contrato com refatoração de persistência na mesma entrega.

Mitigação:

- separar contratos de tela de persistência por fase

### Risco 2

Trocar todas as stores ao mesmo tempo.

Mitigação:

- migração por domínio

### Risco 3

Perder integridade do workflow do aggregate ao persistir estado como simples CRUD.

Mitigação:

- manter regras no domínio
- persistir transições como eventos explícitos

## 9. Resultado esperado

Ao final deste plano:

- o sistema deixa de depender de memória para recursos críticos
- o fluxo real fica auditável
- review, composição e render sobrevivem a restart
- o produto se aproxima do comportamento prometido pela documentação `prd/`
