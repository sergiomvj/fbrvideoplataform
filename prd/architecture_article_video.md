# Arquitetura do Sistema — Motor Editorial de Vídeos Templated

> Baseada em `conceito_geral_article_video.md`, `prd_article_video.md`, `spec_article_video.md`, `interface_ux_article_video.md`, `fbr-arquitetura.md`, `DESIGN_STANDARDS.md` e `securitycoderules.md`  
> Status: Draft arquitetural recomendado  
> Objetivo: definir a melhor arquitetura inicial para o sistema, equilibrando velocidade de execução, consistência operacional e aderência ao padrão FBR

---

## 1. Decisão arquitetural principal

A melhor arquitetura para este sistema, neste momento, é uma **arquitetura modular monolítica com orquestração externa**, organizada assim:

- **Frontend web operacional** em `Next.js 15 + TypeScript + Tailwind + shadcn/ui`
- **Backend principal** em `FastAPI + Python 3.11+`
- **Banco transacional** em `PostgreSQL 16`
- **Cache, filas curtas e locks** em `Redis 7`
- **Orquestração de processos e automações** em `n8n`
- **Camada de agentes/autonomia** no padrão `OpenClaw Gateway`
- **Render externo inicial** via provedor como `HeyGen`
- **Infraestrutura** em `Docker Compose` sobre `VPS Hetzner`, conforme padrão FBR

Essa arquitetura é a melhor opção porque:

1. respeita a arquitetura canônica FBR
2. evita microservices prematuros
3. preserva separação clara entre composição editorial e render externo
4. permite operar rápido com dois templates fechados
5. mantém espaço para evolução futura sem reescrever o núcleo

---

## 2. Forma do sistema

### 2.1 Escolha: monólito modular

O sistema deve nascer como um **monólito modular** e não como microservices.

Motivos:

- o escopo inicial é bem definido
- as regras de negócio são fortemente acopladas ao fluxo editorial
- a complexidade principal está nas decisões do pipeline, não no volume de tráfego entre serviços
- o custo de coordenação entre múltiplos serviços agora seria maior do que o benefício

### 2.2 O que isso significa na prática

Haverá um backend único, mas organizado por domínios funcionais claramente separados.

Domínios iniciais:

- `production-intake`
- `editorial-structuring`
- `visual-planning`
- `media-sourcing`
- `context-verification`
- `human-review`
- `template-composition`
- `render-orchestration`
- `operations-audit`

Essa abordagem dá o melhor dos dois mundos:

- simplicidade operacional de monólito
- disciplina de fronteiras de arquitetura

---

## 3. Princípios arquiteturais obrigatórios

1. **CLI First / Observability Second / UI Third**
   O sistema deve ser operável por backend e automações antes de depender da interface.

2. **Composição editorial é o núcleo**
   O coração da arquitetura não é o render. É a cadeia `entrada -> estrutura -> brief visual -> curadoria -> montagem`.

3. **Automação conservadora**
   Toda decisão automática relevante deve ser auditável e reversível quando aplicável.

4. **Separação entre inteligência e executor**
   O sistema produz a composição e o payload; o provedor externo executa o render.

5. **Orquestração fora do núcleo**
   `n8n` deve coordenar quando fluxos começam, seguem, escalam ou notificam. O backend decide a lógica de domínio.

6. **Frontend como console operacional**
   A UI não concentra a inteligência do fluxo. Ela expõe e controla o estado do sistema.

---

## 4. Arquitetura em camadas

### 4.1 Camada 1 — Interface operacional

Tecnologia:

- `Next.js 15`
- `TypeScript`
- `Tailwind CSS`
- `shadcn/ui`
- `iron-session` para autenticação e sessão

Função:

- cockpit editorial
- criação de produção
- revisão humana
- acompanhamento de estado
- visualização de montagem e render

Regras:

- frontend nunca chama o backend diretamente
- toda chamada passa por rotas autenticadas do próprio Next.js
- a UI deve funcionar como console e não como fonte da verdade

### 4.2 Camada 2 — API gateway do frontend

Tecnologia:

- `Next.js Route Handlers / API Routes`

Função:

- proxy autenticado
- leitura da sessão `iron-session`
- repasse seguro do contexto do usuário
- composição de chamadas para o backend

Isso atende o padrão de `securitycoderules.md`:

- cookie httpOnly
- frontend sem acesso a tokens
- backend recebendo identidade autenticada por header interno controlado

### 4.3 Camada 3 — Backend de domínio

Tecnologia:

- `FastAPI`
- `Pydantic`
- services assíncronos

Função:

- encapsular toda a lógica de domínio
- validar entradas
- coordenar módulos internos
- produzir estados persistidos e payloads finais

Essa camada é a fonte de verdade do sistema.

### 4.4 Camada 4 — Orquestração de fluxo

Tecnologia:

- `n8n`, instância dedicada ao sistema

Função:

- agendar jobs
- disparar pipelines
- reagir a eventos
- coordenar retries de alto nível
- encaminhar revisão humana
- notificar FBR-Click

Regra:

`n8n` orquestra o fluxo, mas não implementa regras de domínio editorial finas.

### 4.5 Camada 5 — Camada de agentes

Tecnologia:

- `OpenClaw Gateway`

Função:

- executar comportamentos autônomos quando o fluxo exigir agente
- suportar tarefas como revisão auxiliar, classificação, explicação de falhas, enriquecimento operacional

Regra crítica:

Como `fbr-arquitetura.md` define OpenClaw como padrão único, o sistema **não deve nascer com LangGraph como framework primário de agentes**, apesar da referência em `securitycoderules.md`.

Resolução arquitetural:

- usar `OpenClaw` como padrão oficial
- usar structured outputs e nós de responsabilidade única como princípio de implementação dos agentes
- tratar a menção a LangGraph como diretriz de qualidade de desenho de agentes, não como obrigação de stack neste sistema

### 4.6 Camada 6 — Persistência

Tecnologia:

- `PostgreSQL 16`
- `Redis 7`

Função do PostgreSQL:

- persistência transacional
- histórico de produções
- estado editorial
- decisões de curadoria
- auditoria

Função do Redis:

- filas leves
- locks distribuídos
- debounce de jobs
- status transitórios
- cache de resultados intermediários
- health/status de camadas LLM, se necessário no padrão FBR

### 4.7 Camada 7 — Integrações externas

Integrações previstas:

- `HeyGen` para render inicial
- bancos de imagem e vídeo
- fontes internas de acervo
- FBR-Click
- provedores LLM

Função:

- permanecer fora do núcleo de domínio
- serem acessadas por adaptadores próprios
- nunca contaminar a lógica central do sistema com contratos externos diretos

---

## 5. Arquitetura lógica do backend

### 5.1 Estrutura de módulos

O backend deve ser organizado por domínios.

Estrutura recomendada:

```text
backend/
  api/
    routes/
      productions.py
      review.py
      templates.py
      media.py
      renders.py
      ops.py
  domain/
    intake/
    structuring/
    visual_planning/
    media_sourcing/
    context_verification/
    human_review/
    composition/
    render/
    audit/
  application/
    services/
    use_cases/
  integrations/
    heygen/
    llm/
    stock_media/
    archive_media/
    fbr_click/
  infrastructure/
    db/
    cache/
    queue/
    settings/
  tests/
```

### 5.2 Regras de fronteira

- `api` valida e roteia
- `application` orquestra casos de uso
- `domain` contém regras de negócio
- `integrations` fala com o mundo externo
- `infrastructure` implementa persistência e recursos técnicos

Isso evita o erro clássico de misturar endpoint, regra de negócio e integração externa no mesmo arquivo.

---

## 6. Fluxo principal de arquitetura

### 6.1 Fluxo automático assistido

1. operador cria produção no frontend
2. Next.js proxy autentica e chama o backend
3. backend registra `production_job`
4. backend dispara caso de uso de estruturação
5. módulo de estrutura editorial gera cenas/blocos
6. módulo de planejamento visual gera `briefs`
7. `n8n` ou serviço interno dispara sourcing de mídia por cena
8. candidatos são avaliados pelo módulo de aderência contextual
9. decisão é persistida:
   - `90–100`: aprovado
   - `60–89`: revisão humana
   - `<60`: reobtenção
10. quando a peça tiver insumos suficientes, módulo de composição gera timeline estruturada
11. adaptador de render transforma isso em payload HeyGen
12. job é enviado
13. status de render é acompanhado
14. resultado final volta para a produção

### 6.2 Fluxo manual guiado

1. operador cria produção em modo manual
2. fornece conteúdo e ativos
3. backend valida compatibilidade desses ativos com o template
4. módulo de composição organiza os ativos na estrutura final
5. se houver inconsistências, produção é bloqueada com feedback explícito
6. payload de render é gerado e enviado

---

## 7. Estratégia de integração com LLM

### 7.1 Papel dos LLMs

Os LLMs devem ser usados apenas onde agregam valor claro:

- estruturação editorial
- geração/refino de brief visual
- reformulação de busca abaixo de 60%
- explicação resumida de falha ou ambiguidade

Eles não devem:

- substituir as regras do template
- decidir fluxo operacional sem guardrails
- aprovar ativos por si mesmos sem política de score e critérios

### 7.2 Estratégia FBR de camadas

Seguir o padrão FBR:

- camada 1: `Ollama` para tarefas de alto volume/classificação quando couber
- camada 2: `Claude API` para raciocínio e geração principal
- camada 3: `GPT-4o` para contingência

### 7.3 Como isso entra no sistema

Criar um adaptador interno `llm_router` no backend, mas com saúde e fallback supervisionados por `n8n` e/ou Redis, conforme padrão FBR.

---

## 8. Estratégia do subsistema de mídia

### 8.1 Separação obrigatória

O subsistema de mídia precisa de quatro componentes separados:

1. `brief builder`
2. `query/prompt builder`
3. `asset sourcing`
4. `context verification`

Não misturar essas quatro responsabilidades é uma decisão arquitetural crítica.

### 8.2 Pipeline recomendado

```text
Scene
  -> Visual Brief
  -> Search Strategy
  -> Candidate Assets
  -> Context Score
  -> Decision
  -> Approved Asset Set
```

### 8.3 Como implementar a verificação

Arquiteturalmente, a verificação contextual deve ser um módulo próprio, não uma função interna do search.

Ele deve produzir:

- score numérico
- breakdown por critério
- flags de conflito
- explicação curta
- decisão sugerida

### 8.4 Human-in-the-loop

O sistema precisa modelar a revisão humana como estado de primeira classe.

Estados possíveis por ativo:

- `auto_approved`
- `human_review_required`
- `rejected_requery`
- `failed_structural`
- `manually_fixed`

Isso facilita auditoria, fila operacional e análise futura.

---

## 9. Modelagem macro de dados

Sem entrar em schema detalhado, a arquitetura pede estas entidades centrais:

- `users`
- `organizations`
- `templates`
- `template_variations`
- `productions`
- `production_inputs`
- `production_scenes`
- `scene_visual_briefs`
- `scene_asset_candidates`
- `scene_asset_scores`
- `scene_asset_decisions`
- `manual_asset_bindings`
- `production_compositions`
- `render_jobs`
- `render_events`
- `audit_events`

### 9.1 Observação importante

O desenho detalhado dessas tabelas deve ser tratado depois com `@data-engineer`, mas essa malha de entidades já orienta corretamente a arquitetura sistêmica.

---

## 10. API design recomendado

### 10.1 Padrão

Usar `REST` no início.

Motivos:

- fluxos são claros e orientados a recurso/estado
- UI operacional se beneficia de endpoints previsíveis
- integração com `n8n` fica simples
- debugging é mais barato do que GraphQL neste estágio

### 10.2 Grupos de endpoint

- `/productions`
- `/productions/{id}/structure`
- `/productions/{id}/media`
- `/productions/{id}/review`
- `/productions/{id}/composition`
- `/productions/{id}/render`
- `/templates`
- `/operations`

### 10.3 Recomendação adicional

Adicionar eventos de transição de estado explícitos, em vez de deixar o frontend montar regras de workflow sozinho.

Exemplo:

- `POST /productions/{id}/submit`
- `POST /productions/{id}/media/requery`
- `POST /productions/{id}/review/{assetId}/approve`
- `POST /productions/{id}/render/start`

---

## 11. Segurança arquitetural

### 11.1 Autenticação

Seguir exatamente o padrão de `securitycoderules.md`:

- `iron-session`
- cookie `httpOnly`
- proxy autenticado no Next.js
- backend sem sessão exposta ao browser

### 11.2 Autorização

Como `securitycoderules.md` enfatiza isolamento por usuário e também fala em RLS, a melhor solução arquitetural é:

- usar PostgreSQL 16 como banco principal
- aplicar isolamento por organização/usuário no backend
- se a escolha final de banco gerenciado recair em Supabase Postgres, ativar RLS como camada adicional

Ou seja:

- **autorização primária**: backend + contexto autenticado
- **autorização reforçada**: RLS se a implementação final usar Supabase

### 11.3 Regras obrigatórias

- validação de input via `Pydantic` em todas as rotas
- rate limiting nas rotas sensíveis
- upload com validação de tipo e tamanho
- mensagens de erro não podem vazar internals
- logs não podem expor dados sensíveis

### 11.4 Segredos

Todos os segredos em `.env` e, idealmente, secret manager da infra no deploy.

---

## 12. Observabilidade

### 12.1 O que observar

O sistema precisa ser observável por produção, cena e ativo.

### 12.2 Métricas mínimas

- produções iniciadas por período
- tempo médio por etapa
- taxa de autoaprovação
- taxa de revisão humana
- taxa de reobtenção
- taxa de falha estrutural
- tempo de render
- falhas por integração externa

### 12.3 Logs

Logs estruturados com:

- `trace_id`
- `production_id`
- `scene_id`
- `asset_id`
- `render_job_id`
- `user_id` ou `organization_id`

### 12.4 Stack

Seguir padrão FBR:

- `Prometheus`
- `Grafana`
- audit log no banco

---

## 13. Integração com FBR-Click

Pelo padrão FBR, eventos relevantes para humanos devem aparecer no FBR-Click.

Este sistema deve publicar pelo menos:

- produção aguardando revisão humana
- falha estrutural de obtenção
- render concluído
- render falhou
- alerta de degradação das camadas LLM

Essa integração não substitui a interface web. Ela amplia o alcance operacional humano.

---

## 14. Infraestrutura recomendada

### 14.1 Ambiente inicial

Uma VPS dedicada com Docker Compose, contendo:

- `frontend`
- `backend`
- `postgres`
- `redis`
- `n8n`
- `openclaw-gateway`
- `nginx`
- `prometheus`
- `grafana`

### 14.2 Motivos

- aderência ao padrão FBR
- custo baixo
- simplicidade de operação
- deploy reproduzível
- ambiente isolado por sistema

### 14.3 Escala futura

Se necessário, a primeira evolução deve ser:

1. separar workers pesados do backend web
2. mover Postgres para instância gerenciada
3. mover Redis para serviço dedicado
4. expandir render/event processing separadamente

Não começar assim.

---

## 15. Decisões que a arquitetura fecha agora

1. **Monólito modular**, não microservices
2. **Next.js + FastAPI + PostgreSQL + Redis**, no padrão FBR
3. **n8n como orquestrador**
4. **OpenClaw como camada oficial de agentes**
5. **REST como API inicial**
6. **HeyGen como render externo inicial**
7. **Context verification como módulo de primeira classe**
8. **Human review como estado nativo do domínio**
9. **Infra em Docker Compose sobre VPS dedicada**

---

## 16. Decisões explicitamente adiadas

1. algoritmo final do score e pesos
2. modelagem detalhada do banco
3. escolha definitiva dos provedores de mídia
4. contratos finais do payload HeyGen
5. desenho detalhado dos agentes OpenClaw
6. política exata de retries por fonte
7. multi-tenant detalhado no nível de billing e isolamento comercial

---

## 17. Risco principal e mitigação

### 17.1 Risco principal

O maior risco não é infraestrutura.

O maior risco é acoplamento incorreto entre:

- estrutura narrativa
- sourcing de mídia
- score contextual
- montagem final

### 17.2 Mitigação arquitetural

Mitigar isso com:

- módulos separados
- contratos claros entre etapas
- persistência de estado intermediário
- revisão humana modelada explicitamente
- observabilidade por cena e ativo

---

## 18. Recomendação final do arquiteto

Se o objetivo é construir o sistema certo na terceira tentativa, a melhor escolha é:

**um sistema FBR-canônico, modular, com backend forte em domínio, UI operacional clara, n8n para orquestração, OpenClaw para autonomia, e integrações externas tratadas como adaptadores periféricos.**

Essa arquitetura é conservadora onde precisa ser, forte no núcleo que realmente diferencia o produto, e suficientemente flexível para crescer depois sem desmontar a base.

