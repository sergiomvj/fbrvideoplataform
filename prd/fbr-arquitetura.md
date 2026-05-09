# FBR Arquitetura de Sistemas — Bíblia FBR v1.0
> **Fonte canônica de verdade para todos os sistemas FBR.**
> Todo agente que trabalhar em qualquer projeto FBR deve carregar este arquivo como contexto primário.
> Qualquer decisão técnica que contradiga este documento requer aprovação explícita do Arquiteto FBR.

---

## PRESSUPOSTOS INEGOCIÁVEIS

Estes pressupostos não são preferências — são restrições absolutas. O agente NUNCA deve propor arquiteturas que os violem.

### Pressuposto 1 — OpenClaw é o padrão único de agentes

- Todos os agentes autônomos FBR são implementados sobre o OpenClaw Gateway (Node.js, MIT)
- Proibido usar CrewAI, AutoGen, LangGraph ou qualquer outro framework de agentes
- Todo agente FBR é definido por exatamente 7 arquivos Markdown versionados em Git
- Se não tem SOUL.md, não é um agente FBR

**Os 7 Markdowns obrigatórios de todo agente:**

| Arquivo | Conteúdo | Regra crítica |
|---------|----------|---------------|
| SOUL.md | Identidade, valores, restrições éticas absolutas | Carregado PRIMEIRO. Nada sobrescreve. |
| IDENTITY.md | Nome, role, objetivos, LLM primário e fallback | Usado pelo FBR-Click para o card de perfil |
| TASKS.md | Tarefas recorrentes e triggers de evento | Arquivo mais editado na evolução do agente |
| AGENTS.md | Scope de canais, limites de autonomia, prioridades | Define onde e como o agente pode agir |
| MEMORY.md | Fatos duráveis sobre o contexto operacional | Atualizado pelo agente ao final de sessões relevantes |
| TOOLS.md | APIs, skills e ferramentas externas disponíveis | Referenciado ao executar ações |
| USER.md | Preferências do time, contexto da empresa | Camada de personalização sobre a identidade |

### Pressuposto 2 — n8n é o sistema nervoso central

- n8n é a plataforma de orquestração de todos os fluxos FBR
- Cada sistema tem sua própria instância n8n isolada
- n8n decide QUANDO e POR QUÊ um agente é chamado
- OpenClaw decide O QUÊ o agente faz quando chamado
- Os dois NÃO se substituem — são camadas distintas

### Pressuposto 3 — Todo agente tem um humano responsável e limites explícitos

- Nenhum agente opera sem um owner humano designado
- Todo agente tem lista explícita de ações que requerem aprovação humana (em AGENTS.md)
- Essa lista NUNCA pode estar vazia
- Toda ação irreversível requer aprovação humana: deletar dados, enviar comunicação externa, fechar negócios, deploy em produção

### Pressuposto 4 — LLM em três camadas com fallback automático

```
Camada 1 — Ollama (Mac Mini M4 32GB via Tailscale)
  → Uso: tarefas de alto volume, classificação, scoring
  → Timeout: 15s
  → Fallback: se offline > 30s → Camada 2 automático

Camada 2 — Claude API (claude-sonnet-4-6)
  → Uso: geração de conteúdo, raciocínio complexo, personalização
  → Timeout: 30s
  → Fallback: se rate limit ou erro → Camada 3

Camada 3 — GPT-4o API (reserva)
  → Uso: contingência total, nunca primária
  → Timeout: 30s
  → Fallback: alerta crítico para owner
```

- n8n faz health check nas três camadas a cada 60s e publica status no Redis
- O módulo llm.py lê o status do Redis antes de cada chamada (sem latência de health check no caminho crítico)
- Indisponibilidade de qualquer camada não interrompe a operação — degrada de forma controlada

### Pressuposto 5 — FBR-Click é o hub central de todos os sistemas

- Todo evento relevante para um humano se manifesta no FBR-Click
- Cada sistema tem um canal dedicado no FBR-Click
- Agentes dos sistemas aparecem como membros do FBR-Click (não como webhooks anônimos)
- Humanos interagem com todos os sistemas pela mesma superfície: o FBR-Click
- Se um evento só precisa ser logado → fica nos logs do sistema de origem
- Se um evento é relevante para um humano → obrigatoriamente aparece no FBR-Click

---

## ARQUITETURA CANÔNICA

Todo sistema FBR implementa estas camadas na mesma ordem:

```
┌─────────────────────────────────────────────┐
│  FBR-Click (canal dedicado por sistema)     │  ← Interface humana única
├─────────────────────────────────────────────┤
│  n8n (instância dedicada por sistema)       │  ← Orquestração de fluxos
├─────────────────────────────────────────────┤
│  OpenClaw Gateway + Times de agentes        │  ← Execução autônoma
├─────────────────────────────────────────────┤
│  Git (repositório por agente, 7 Markdowns)  │  ← Configuração versionada
├─────────────────────────────────────────────┤
│  PostgreSQL 16 + Redis 7                    │  ← Persistência e filas
├─────────────────────────────────────────────┤
│  Ollama → Claude API → GPT-4o               │  ← LLM em cascata
├─────────────────────────────────────────────┤
│  VPS Hetzner + Docker Compose + Tailscale   │  ← Infraestrutura
├─────────────────────────────────────────────┤
│  Grafana + Prometheus + Audit Log           │  ← Monitoramento
└─────────────────────────────────────────────┘
```

### Princípios de isolamento

- Cada sistema roda em sua própria VPS isolada
- Comunicação entre sistemas: REST API autenticada com JWT ou via FBR-Click
- PROIBIDO: acesso direto a banco de dados cruzado entre sistemas
- Uma falha em um sistema não deve cascadear para outros

### Protocolos de comunicação por tipo

| Tipo | Mecanismo |
|------|-----------|
| Sistema → Humano | FBR-Click (agente posta no canal) |
| Sistema → Sistema | REST API com JWT |
| Sistema → LLM | OpenClaw Gateway (camada de abstração obrigatória) |
| Humano → Sistema | FBR-Click (mensagem ou tarefa para agente) |
| Agente → Agente | Via n8n (message broker interno) |

---

## STACK TECNOLÓGICA PADRÃO

Todo sistema FBR usa esta stack. Desvios requerem justificativa explícita:

| Componente | Tecnologia | Versão |
|------------|-----------|--------|
| Backend | FastAPI + Python | 3.11+ |
| Frontend | Next.js + TypeScript + Tailwind + shadcn/ui | 15 |
| Banco de dados | PostgreSQL | 16 |
| Cache e filas | Redis | 7 |
| Orquestração | n8n | instância dedicada por sistema |
| Agentes | OpenClaw Gateway | Node.js · MIT |
| Containerização | Docker + Docker Compose | — |
| Proxy reverso | Nginx + Certbot | — |
| Rede privada | Tailscale | — |
| Monitoramento | Grafana + Prometheus | — |
| Auth frontend | iron-session | cookie httpOnly |

---

## SISTEMAS FBR EXISTENTES

| Sistema | Propósito | Canal FBR-Click | Agente de handoff |
|---------|-----------|-----------------|-------------------|
| FBR-Click | Hub central de colaboração humanos + agentes | — (é o hub) | — |
| FBR-Leads | Captação, enriquecimento e aquecimento de leads | #leads-qualificados | Cadenciador Bot |
| FBR-Dev | Gestão de projetos de desenvolvimento com agentes | #dev-sprints | Sprint Bot |
| FBR-Suporte | Suporte comercial pré e pós-venda multicanal | #suporte-comercial | Suporte Bot |

---

## REGRAS DE GOVERNANÇA DE AGENTES

### Processo obrigatório para criar um novo agente (6 passos)

1. Owner define propósito e limites de autonomia
2. Owner cria repositório Git e preenche os 7 Markdowns — SOUL.md primeiro
3. Pull Request obrigatório: outro owner ou Arquiteto revisa antes de ativar
4. Registro no FBR-Click: admin informa URL do repositório — plataforma valida o schema
5. Período de observação: primeiros 7 dias com monitoramento ativo e kill switch pronto
6. Aprovação formal de operação plena pelo Owner do sistema

**Nenhuma exceção, mesmo para protótipos ou testes.**

### Papéis e responsabilidades

| Papel | Responsabilidades |
|-------|-------------------|
| Arquiteto FBR | Guardião deste documento. Aprova mudanças nos pressupostos. |
| Owner de Sistema | Responsável por um sistema. Define e mantém os agentes. |
| Owner de Agente | Configura os 7 Markdowns. Tem o kill switch. |
| Operador | Usa o FBR-Click para dar instruções e aprovar ações. |
| Auditor | Revisão mensal dos audit logs. Reporta anomalias. |

---

## REFERÊNCIAS CRUZADAS

- Segurança e qualidade de código: `docs/securitycoderules.md`
- PRD completo do FBR-Leads: `docs/fbr-leads-prd.md`
- Estrutura de PRD e implementation plan: workflow `/build-saas`
