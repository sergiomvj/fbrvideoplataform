# QA Remediation Backlog

## 1. Objetivo

Este documento transforma os findings da revisão técnica em um backlog de correção detalhado, organizado para execução por múltiplos devs sem conflito de fronteiras.

Ele não substitui os stories originais. Ele funciona como um pacote de correção transversal para fechar gaps entre:

- stories marcados como implementados
- comportamento real do código
- arquitetura e requisitos descritos na pasta `prd`

## 2. Princípios de execução

1. Nenhuma task deve alterar contratos fora do seu escopo sem registrar decisão cruzada.
2. Correções de segurança e integridade têm prioridade sobre UX e documentação.
3. Toda task precisa fechar backend, frontend, testes e documentação do seu escopo.
4. Toda correção deve preservar auditabilidade e preparar persistência real em PostgreSQL.
5. Onde houver mismatch de contrato, o contrato oficial deve ser explicitamente redefinido antes da implementação.

## 3. Mapa dos findings de origem

- `F-01` Autenticação insegura e impersonação arbitrária
- `F-02` Fila de revisão humana quebrada por incompatibilidade entre frontend e backend
- `F-03` Tela de detalhe de produção incompatível com o payload real
- `F-04` Estado operacional volátil em memória
- `F-05` Fluxo manual guiado incompleto
- `F-06` Navegação frontend aponta para rotas inexistentes
- `F-07` Documentação técnica e padrões visuais divergentes da documentação base

## 4. Frentes de correção

### Epic R1 - Security & Identity Hardening

#### Task R1.1 - Replace Fake Session Bootstrap

**Objetivo**

Remover o login automático com `current-user` e substituir por uma estratégia de autenticação coerente com a arquitetura aprovada.

**Problema**

Hoje o frontend cria sessão autenticada sem verificação real e o backend aceita qualquer `X-User-Id`.

**Escopo**

- remover bootstrap fake da sessão
- impedir criação de sessão por payload arbitrário
- definir origem confiável da identidade no gateway
- bloquear impersonação entre frontend e backend

**Arquivos prováveis**

- `frontend/app/api/auth/session/route.ts`
- `frontend/app/productions/new/page.tsx`
- `frontend/lib/session/index.ts`
- `frontend/lib/gateway/index.ts`
- `backend/application/security/auth.py`

**Critérios de aceite**

- frontend não cria sessão autenticada com `userId` livre
- backend não aceita identidade arbitrária enviada diretamente pelo cliente
- requests sem sessão válida retornam `401`
- identidade autenticada é propagada por caminho controlado e verificável
- existe teste positivo e negativo para autenticação

**Dependências**

- nenhuma

**Risco**

- alto, envolve toda a superfície autenticada do sistema

---

#### Task R1.2 - Define Auth Contract for Operator Context

**Objetivo**

Fechar o contrato mínimo de autenticação/autorização para o MVP, incluindo operador, organização e escopo.

**Escopo**

- definir shape do contexto autenticado
- definir campos mínimos de sessão
- definir regra de isolamento por usuário e organização
- documentar como backend recebe identidade autenticada

**Critérios de aceite**

- existe contrato explícito do contexto autenticado
- o contrato é usado pelo gateway e pelo backend
- documentação complementar é atualizada

**Dependências**

- `R1.1`

---

### Epic R2 - Review Queue Contract Repair

#### Task R2.1 - Normalize Review Queue API Contract

**Objetivo**

Alinhar o contrato do backend de revisão humana com as necessidades reais da UI e com o modelo funcional do produto.

**Problema**

O backend retorna um shape incompleto e incompatível com o componente de review.

**Escopo**

- redefinir payload de listagem de review
- incluir campos de cena, score, justificativa e preview
- definir ações suportadas: approve, reject e requery
- definir status permitidos do item

**Arquivos prováveis**

- `backend/api/routes/review.py`
- `backend/domain/human_review/*`
- `backend/application/services/*` relacionados
- `docs/*` de contrato se necessário

**Critérios de aceite**

- o endpoint de review devolve dados suficientes para renderização completa da UI
- o endpoint suporta as ações expostas pela interface
- há contrato documentado do payload
- testes cobrem listagem e transições de ação

**Dependências**

- `R1.1`
- `R4.1` quando a persistência real entrar

---

#### Task R2.2 - Repair Frontend Review Workspace

**Objetivo**

Corrigir a tela `/review` para consumir o contrato oficial do backend e operar de forma funcional.

**Escopo**

- corrigir obtenção de `production_id`
- corrigir URLs de approve/reject/requery
- ajustar shape de dados do componente `ReviewItem`
- renderizar preview de asset quando houver URL
- tratar estados vazios, erro e processamento

**Arquivos prováveis**

- `frontend/app/review/page.tsx`
- `frontend/components/review-queue/review-item.tsx`
- `frontend/components/review-queue/review-actions.tsx`
- `frontend/components/review-queue/score-badge.tsx`

**Critérios de aceite**

- a tela carrega fila real sem erro de contrato
- ações disparam endpoints corretos
- `requery` só aparece se houver backend correspondente
- lint passa sem warnings estruturais relevantes

**Dependências**

- `R2.1`

---

### Epic R3 - Production Detail Contract Repair

#### Task R3.1 - Define Canonical Production Detail Payload

**Objetivo**

Definir o payload canônico da tela de detalhe da produção, integrando estado, composição e render.

**Escopo**

- fechar shape da resposta de detalhe
- incluir estado atual, histórico, template/variação, composição e render
- definir o que é resumo e o que é detalhe

**Arquivos prováveis**

- `backend/api/routes/productions.py`
- `api/schemas/*`
- `docs/production-workflow-model.md`

**Critérios de aceite**

- payload de detalhe está explicitamente definido
- o backend o produz de forma consistente
- a UI consegue consumir sem inferências ad hoc

**Dependências**

- `R4.1`
- `R4.2`
- `R4.3`

---

#### Task R3.2 - Repair Production Detail Screen

**Objetivo**

Adequar a UI `/productions/[id]` ao contrato oficial de detalhe.

**Escopo**

- corrigir nomes de campos
- renderizar histórico real de estados
- renderizar preview de composição real
- renderizar status de render sem campos inventados

**Arquivos prováveis**

- `frontend/app/productions/[id]/page.tsx`
- `frontend/components/production-detail/*`

**Critérios de aceite**

- tela não depende de campos inexistentes
- preview e render status usam payload oficial
- fluxo visual continua funcional e consistente

**Dependências**

- `R3.1`

---

### Epic R4 - Persistence & Complete Historical Trace

#### Task R4.1 - Persist Core Production Aggregate in PostgreSQL

**Objetivo**

Trocar o armazenamento em memória de produção por persistência transacional em PostgreSQL.

**Escopo**

- persistir produção
- persistir input normalizado
- persistir estado atual
- persistir histórico de transições
- manter compatibilidade com o domínio existente

**Arquivos prováveis**

- `backend/api/routes/productions.py`
- `backend/domain/production/*`
- `backend/infrastructure/db/*`
- migrations futuras

**Critérios de aceite**

- produções sobrevivem a restart do backend
- histórico de transições permanece íntegro
- listagem por usuário continua funcionando
- testes cobrem criação, leitura e transição

**Dependências**

- modelo de banco consolidado

---

#### Task R4.2 - Persist Composition and Render Lifecycle

**Objetivo**

Persistir composições e jobs de render para eliminar stores voláteis.

**Escopo**

- remover `_composition_store` em memória
- persistir composição final e slots
- persistir render jobs e eventos de render
- suportar polling confiável de status

**Arquivos prováveis**

- `backend/api/routes/renders.py`
- `backend/domain/render/models.py`
- `backend/domain/composition/*`
- `backend/integrations/heygen/*`

**Critérios de aceite**

- composição e render job sobrevivem a restart
- tela de detalhe consegue consultar render real
- existe histórico de eventos do job

**Dependências**

- `R4.1`

---

#### Task R4.3 - Persist Review Queue, Scores and Decisions

**Objetivo**

Persistir o subsistema de curadoria e decisão contextual.

**Escopo**

- persistir candidatos de mídia
- persistir score breakdown
- persistir decisão operacional
- persistir review queue items
- persistir ações humanas

**Critérios de aceite**

- cada cena tem rastreabilidade completa do candidato até a decisão final
- é possível auditar quem aprovou/rejeitou/requereu novo sourcing
- review queue deixa de ser efêmera

**Dependências**

- modelo de banco consolidado

---

### Epic R5 - Manual Guided Flow Completion

#### Task R5.1 - Define Manual Pre-Flow Contract

**Objetivo**

Fechar o contrato do modo manual guiado conforme `Conceito Geral`, `PRD` e `SPEC`.

**Escopo**

- definir quais insumos manuais o operador informa
- definir ativos obrigatórios, fixos, preferidos e proibidos
- definir vinculação por cena ou bloco
- definir regras de validação de compatibilidade com template

**Critérios de aceite**

- contrato explícito de pré-fluxo manual publicado
- backend e frontend trabalham sobre o mesmo contrato

**Dependências**

- nenhuma

---

#### Task R5.2 - Expose Manual Binding APIs

**Objetivo**

Transformar o serviço de manual binding existente em API funcional.

**Escopo**

- criar endpoints de create/list/remove binding
- validar autoridade do operador
- validar compatibilidade estrutural
- registrar auditoria da ação manual

**Critérios de aceite**

- bindings manuais podem ser criados, listados e removidos
- auditoria registra quem fez o override
- composição consome o binding persistido

**Dependências**

- `R5.1`
- `R4.3`

---

#### Task R5.3 - Extend Production Wizard for Manual Guided Mode

**Objetivo**

Fechar a lacuna do frontend para o modo manual guiado.

**Escopo**

- adicionar fase pré-fluxo no wizard
- permitir associação manual de ativos
- permitir indicar obrigatórios/proibidos
- diferenciar claramente modo automático de manual

**Arquivos prováveis**

- `frontend/app/productions/new/page.tsx`
- `frontend/components/production-wizard/*`

**Critérios de aceite**

- modo manual possui experiência própria
- operador consegue informar ativos antes da montagem
- submissão respeita o contrato manual oficial

**Dependências**

- `R5.1`
- `R5.2`

---

### Epic R6 - Navigation, UX and Frontend Standards Repair

#### Task R6.1 - Remove or Implement Dead Navigation Targets

**Objetivo**

Eliminar navegação para rotas inexistentes.

**Escopo**

- decidir se `/dashboard`, `/productions`, `/templates` e `/settings` serão implementadas agora ou removidas temporariamente
- ajustar sidebar ao recorte real do produto

**Critérios de aceite**

- nenhum link principal do shell aponta para rota inexistente
- a navegação reflete o estado real do produto

**Dependências**

- nenhuma

---

#### Task R6.2 - Align Frontend Typography and Metadata with Design Standards

**Objetivo**

Adequar o shell visual ao padrão de design definido em `prd/DESIGN_STANDARDS.md`.

**Escopo**

- trocar `Geist` por tipografia aprovada ou justificar exceção formal
- ajustar metadata e idioma base
- alinhar tokens de fonte com o padrão definido

**Critérios de aceite**

- layout base reflete o padrão documental aprovado
- metadata não permanece genérica

**Dependências**

- nenhuma

---

#### Task R6.3 - Clean Frontend Lint Debt

**Objetivo**

Zerar os erros atuais de lint e os avisos estruturais mais importantes.

**Escopo**

- corrigir `setState` em effect
- remover interfaces vazias
- eliminar imports não usados

**Critérios de aceite**

- `npm run lint` passa

**Dependências**

- nenhuma

---

### Epic R7 - Technical Documentation & Operational Help

#### Task R7.1 - Replace Placeholder Frontend README

**Objetivo**

Trocar o README padrão do Next por documentação real do módulo frontend.

**Escopo**

- visão do frontend
- rotas existentes
- integração com backend
- autenticação
- comandos de desenvolvimento
- limitações conhecidas

**Critérios de aceite**

- `frontend/README.md` documenta o módulo real
- não permanece template genérico

**Dependências**

- nenhuma

---

#### Task R7.2 - Create Backend Technical README

**Objetivo**

Adicionar onboarding técnico mínimo ao backend.

**Escopo**

- arquitetura modular
- rotas
- serviços principais
- dependências locais
- como rodar testes
- limitações conhecidas

**Critérios de aceite**

- existe `backend/README.md`
- onboarding mínimo é suficiente para um dev novo subir entendimento

**Dependências**

- nenhuma

---

#### Task R7.3 - Reconcile Functional Help with Actual Product State

**Objetivo**

Manter o help funcional sincronizado com as correções feitas.

**Escopo**

- revisar `docs/help-completo-funcionalidades.md`
- atualizar fluxos, rotas e limitações
- explicitar o que está pronto, parcial e futuro

**Critérios de aceite**

- help não promete o que o sistema ainda não entrega
- help descreve o sistema corrigido

**Dependências**

- tasks das frentes corrigidas

## 5. Ordem recomendada

### Onda 1 - Bloqueios reais

- `R1.1`
- `R1.2`
- `R2.1`
- `R6.3`

### Onda 2 - Persistência estruturante

- `R4.1`
- `R4.2`
- `R4.3`

### Onda 3 - Contratos de tela

- `R2.2`
- `R3.1`
- `R3.2`

### Onda 4 - Fluxo manual

- `R5.1`
- `R5.2`
- `R5.3`

### Onda 5 - UX e documentação

- `R6.1`
- `R6.2`
- `R7.1`
- `R7.2`
- `R7.3`

## 6. Paralelização segura

### Lane A - Security / Gateway

- `R1.1`
- `R1.2`

### Lane B - Persistence / Backend Domain

- `R4.1`
- `R4.2`
- `R4.3`
- `R3.1`

### Lane C - Frontend Contracts / UX

- `R2.2`
- `R3.2`
- `R5.3`
- `R6.1`
- `R6.2`
- `R6.3`

### Lane D - Manual Flow / Review

- `R2.1`
- `R5.1`
- `R5.2`

### Lane E - Documentation

- `R7.1`
- `R7.2`
- `R7.3`

## 7. Definição de pronto global

Uma correção só deve ser considerada concluída quando:

- o comportamento do código estiver alinhado ao contrato aprovado
- lint e build do frontend passarem
- testes relevantes do backend existirem e passarem no ambiente preparado
- o help e/ou README do escopo estiverem atualizados
- não houver mais dependência de store em memória para o recurso corrigido, quando a task atacar persistência
