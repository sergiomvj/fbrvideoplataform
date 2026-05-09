# Interface UX/UI — Motor Editorial de Vídeos Templated

> Baseada em `DESIGN_STANDARDS.md`, `conceito_geral_article_video.md`, `prd_article_video.md` e `spec_article_video.md`  
> Status: Draft de definição de interface  
> Objetivo: definir uma interface bonita, eficaz e operacionalmente segura para o sistema

---

## 1. Objetivo da interface

A interface deve permitir que um operador editorial use o sistema com rapidez, confiança e clareza, sem transformar o produto em uma ferramenta criativa caótica.

O sistema não é um editor livre. Portanto, a interface também não deve parecer um editor livre.

Ela deve comunicar:

- controle
- clareza operacional
- confiança nas decisões automáticas
- revisão humana nos pontos certos
- fluidez entre fluxo automático e fluxo manual

---

## 2. Princípios de UX da interface

### 2.1 Clareza acima de exuberância

A interface deve ser visualmente forte, mas sempre subordinada à compreensão do fluxo.

### 2.2 O sistema deve parecer confiável

Como o produto lida com automação, score de aderência e revisão editorial, a interface precisa transmitir precisão e governança.

### 2.3 O usuário sempre deve saber em que etapa está

O operador nunca pode se sentir perdido entre entrada, estruturação, mídia, revisão e render.

### 2.4 Automação deve ser auditável

Toda decisão automática relevante precisa ser visível, explicável e reversível quando aplicável.

### 2.5 Modo manual não é fallback feio

O fluxo manual deve ter tratamento de primeira classe, com boa ergonomia e sem parecer “gambiarra operacional”.

---

## 3. Direção visual

### 3.1 Personalidade visual

A interface deve combinar:

- sobriedade editorial
- energia de produto moderno
- sensação de sala de controle audiovisual

Em vez de parecer uma dashboard administrativa genérica, ela deve lembrar uma bancada editorial contemporânea: limpa, profunda e precisa.

### 3.2 Linguagem estética

- base escura rica para áreas operacionais densas
- superfícies claras e bem organizadas para formulários e leitura
- laranja de marca como cor de ação e energia
- contraste alto e disciplinado
- tipografia contemporânea, técnica e editorial

### 3.3 Sensação desejada

O usuário deve sentir:

- “eu sei o que está acontecendo”
- “o sistema está me ajudando, não me confundindo”
- “as decisões automáticas são transparentes”
- “o fluxo manual é poderoso e controlado”

---

## 4. Tokens visuais derivados do Design Standards

### 4.1 Tipografia

Com base em `DESIGN_STANDARDS.md`:

- Logo: `Outfit` ou `Montserrat`
- Headings: `Outfit`
- Corpo e interface: `Inter`

Aplicação recomendada:

- `H1`: Outfit 700
- `H2`: Outfit 600
- `H3`: Outfit 600
- labels e navegação: Inter 500
- corpo e inputs: Inter 400

### 4.2 Paleta principal

#### Base clara

- `background-app`: `#F8FAFC`
- `surface-card`: `#FFFFFF`
- `border-soft`: `#E2E8F0`
- `text-primary`: `#0F172A`
- `text-secondary`: `#475569`

#### Base escura

- `background-deep`: `#101622`
- `background-panel`: `#151B2B`
- `surface-dark-card`: `#1E293B`
- `text-on-dark`: `#F8FAFC`
- `text-dark-muted`: `#94A3B8`

#### Marca

- `brand-primary`: `#F97316`
- `brand-primary-hover`: `#EA580C`
- `brand-accent`: `#FCD34D`

#### Estados semânticos

- `success`: `#16A34A`
- `warning`: `#D97706`
- `danger`: `#DC2626`
- `info`: `#2563EB`

### 4.3 Uso de cor por função

- laranja: ações principais, seleção ativa, progresso
- verde: material autoaprovado, status seguros
- âmbar: revisão humana, atenção moderada
- vermelho: rejeição, falha estrutural, conflito contextual
- azul: informações auxiliares, contexto, detalhes técnicos

---

## 5. Arquitetura geral da interface

### 5.1 Estrutura de navegação

A estrutura ideal é:

1. navegação lateral persistente
2. cabeçalho superior contextual
3. área central de trabalho
4. painel lateral contextual opcional para detalhes, score, mídia ou auditoria

### 5.2 Navegação principal

Itens principais:

- `Nova Produção`
- `Fila de Revisão`
- `Produções`
- `Templates`
- `Mídia`
- `Configurações`

### 5.3 Navegação secundária contextual

Dentro de uma produção ativa:

- `Entrada`
- `Estrutura`
- `Mídia`
- `Revisão`
- `Montagem`
- `Render`

Isso deve aparecer como stepper horizontal ou barra de progresso segmentada.

---

## 6. Tela principal do sistema

### 6.1 Home operacional

A primeira tela após login deve funcionar como um cockpit editorial.

Conteúdo principal:

- bloco de ação rápida para iniciar produção
- cards de status do dia
- fila de revisão pendente
- últimas produções
- indicadores de confiança automática

### 6.2 Estrutura visual da home

#### Faixa superior

- título: `Central de Produção`
- subtítulo curto com contexto operacional
- CTA principal: `Nova Produção`

#### Linha de métricas

Quatro cards:

- `Produções em andamento`
- `Aguardando revisão`
- `Autoaprovadas hoje`
- `Falhas de obtenção`

#### Bloco esquerdo principal

- lista de produções em curso
- status por etapa
- template usado
- modo de operação

#### Bloco direito

- revisão prioritária
- alertas de baixa aderência
- recomendações operacionais

### 6.3 Estilo dessa tela

- fundo geral claro
- blocos importantes em branco
- área de revisão com destaque âmbar suave
- cards de decisão automática com pequenos indicadores coloridos

---

## 7. Tela “Nova Produção”

Essa é a tela mais importante do produto.

Ela precisa ser elegante, extremamente clara e orientada por decisão.

### 7.1 Objetivo

Permitir que o usuário inicie uma nova peça sem dúvida sobre:

- qual template escolher
- qual modo usar
- qual conteúdo fornecer
- o que acontecerá depois

### 7.2 Estrutura ideal

#### Bloco 1 — Escolha do modo

Dois cards grandes lado a lado:

- `Automático Assistido`
- `Manual Guiado`

Cada card deve explicar:

- quando usar
- nível de controle
- nível de automação

Visual:

- card com borda forte ao selecionar
- ícone ou ilustração simples
- resumo em 2 linhas

#### Bloco 2 — Escolha do template

Dois cards visuais:

- `Presenter Short`
- `VideoDoc Narrated`

Cada card deve mostrar:

- formato
- duração máxima
- lógica visual
- pequena miniatura de composição

#### Bloco 3 — Escolha da variação

Controle simples e visual:

- `Variação 1`
- `Variação 2`
- `Variação 3`

Cada uma com thumbnail pequena para evidenciar diferença de abertura/composição.

#### Bloco 4 — Entrada de conteúdo

Tabs ou segmented control:

- `Artigo`
- `Texto Base`
- `Roteiro`

Dependendo do modo manual:

- área adicional para upload ou associação de ativos visuais

#### Bloco 5 — Resumo da configuração

Box fixo lateral ou rodapé sticky com:

- modo selecionado
- template
- variação
- duração alvo
- tipo de entrada
- CTA principal: `Continuar`

---

## 8. Tela de estruturação editorial

### 8.1 Função

Mostrar como o conteúdo foi organizado dentro do template antes de entrar na fase de mídia.

### 8.2 Estrutura

- coluna esquerda: cenas ou blocos em ordem
- centro: detalhes da cena selecionada
- direita: resumo do template e validações

### 8.3 Para cada cena

A interface deve exibir:

- nome da cena
- papel narrativo
- texto/narração
- duração estimada
- função visual esperada

### 8.4 Comportamento

No fluxo automático:

- o usuário acompanha e revisa

No fluxo manual:

- o usuário pode associar ou ajustar os insumos da cena antes da montagem

---

## 9. Tela de mídia

Essa será a área mais crítica e precisa da interface.

Ela não deve parecer uma galeria caótica.

Ela deve parecer uma mesa de curadoria.

### 9.1 Estrutura recomendada

#### Coluna esquerda

Lista de cenas:

- cena atual destacada
- score médio da cena
- status da obtenção

#### Painel central

Candidatos de mídia para a cena selecionada

Cada candidato deve mostrar:

- thumbnail forte
- tipo do ativo
- origem
- score de aderência
- status operacional

#### Painel direito

Ficha de avaliação:

- brief visual da cena
- justificativa do score
- conflitos detectados
- motivo da aprovação/rejeição

### 9.2 Estados visuais dos candidatos

- `90–100`: borda verde + selo `Autoaprovado`
- `60–89`: borda âmbar + selo `Revisão necessária`
- `<60`: borda vermelha + selo `Reobter`

### 9.3 Interações importantes

O usuário deve poder:

- aprovar manualmente candidato plausível
- rejeitar ativo
- fixar ativo no modo manual
- ver por que o score foi calculado daquele modo
- solicitar nova busca

### 9.4 Componente-chave: Score Ring

Cada ativo deve ter um indicador circular ou badge grande de score.

Exemplo:

- `94` em verde
- `78` em âmbar
- `42` em vermelho

Isso deve ser um elemento visual central do sistema, porque confiança contextual é uma das ideias-mãe do produto.

---

## 10. Tela de revisão humana

### 10.1 Função

Ser a fila de triagem editorial dos materiais que ficaram entre `60` e `89`.

### 10.2 Estrutura

Tabela ou lista densa com:

- produção
- cena
- template
- score
- tipo de conflito
- data/hora
- prioridade

### 10.3 Ao abrir um item

Mostrar lado a lado:

- brief da cena
- mídia candidata
- justificativa do sistema
- ações: `Aprovar`, `Substituir`, `Rejeitar`, `Mandar reobter`

### 10.4 Objetivo de UX

A revisão deve ser rápida.

O operador não deve precisar “descobrir sozinho” o problema. O sistema precisa expor o racional da triagem.

---

## 11. Tela de montagem final

### 11.1 Função

Exibir a composição consolidada antes do render.

### 11.2 Estrutura

- preview central da peça
- timeline lateral ou inferior
- lista das cenas com seus ativos aprovados
- resumo técnico do job

### 11.3 No Presenter Short

Mostrar:

- avatar escolhido
- fundo institucional
- blocos narrativos
- variação aplicada

### 11.4 No VideoDoc Narrated

Mostrar:

- sequência de mídias
- blocos narrativos
- presença do apresentador/narração
- duração consolidada

---

## 12. Tela de produções

### 12.1 Objetivo

Dar visão histórica e operacional das produções.

### 12.2 Estrutura

Tabela com filtros por:

- status
- template
- modo de operação
- data
- autoaprovadas
- revisadas manualmente

### 12.3 Informações por linha

- título da produção
- template
- modo
- etapa atual
- score médio da mídia
- situação do render
- data

---

## 13. Tela de templates

### 13.1 Objetivo

Permitir entendimento e governança dos templates disponíveis.

### 13.2 Conteúdo

Para cada template:

- descrição
- formato
- duração
- variações
- regras estruturais
- preview estático do layout base

### 13.3 Importância

Essa tela ajuda a reforçar que o sistema trabalha com formatos controlados, não com composição livre.

---

## 14. Tela de mídia e regras de obtenção

### 14.1 Objetivo

Oferecer visão mais estratégica sobre sourcing e curadoria visual.

### 14.2 Conteúdo recomendado

- status das fontes de mídia
- taxa média de aprovação automática
- taxa de retrabalho
- falhas estruturais por tipo de cena
- ativos manuais mais reutilizados

---

## 15. Componentes principais do design system

### 15.1 Atoms

- button
- input
- textarea
- select
- badge
- tag
- icon
- divider
- tooltip

### 15.2 Molecules

- template card
- mode selector card
- score badge
- score ring
- asset card
- scene item
- status pill
- filter bar
- stepper

### 15.3 Organisms

- production cockpit
- new production wizard
- media curation board
- human review queue
- final assembly preview
- template catalog

---

## 16. Padrões de interação

### 16.1 Wizard orientado por etapas

Para criação de produção, usar fluxo em etapas:

1. modo
2. template
3. variação
4. entrada
5. estrutura
6. mídia
7. revisão
8. montagem
9. render

### 16.2 Densidade progressiva

- começo do fluxo: interface mais simples e guiada
- fases de mídia e revisão: maior densidade informacional
- montagem final: foco em validação e confiança

### 16.3 Feedback visual

Toda ação importante deve ter retorno claro:

- seleção de template
- mudança de modo
- aprovação de ativo
- rejeição
- reobtenção
- envio a render

---

## 17. Motion e microinterações

Usar motion com moderação e propósito.

### 17.1 Recomendações

- fade/slide curto entre etapas do wizard
- hover suave em cards de template e modo
- animação de score ring ao carregar resultados
- shimmer leve para ativos em busca
- transição clara ao mover item para revisão humana

### 17.2 O que evitar

- animações decorativas demais
- excesso de glassmorphism
- movimento constante em áreas operacionais

---

## 18. Acessibilidade

Com base no `DESIGN_STANDARDS.md`, a interface deve seguir no mínimo WCAG AA.

### 18.1 Regras mínimas

- contraste mínimo `4.5:1`
- estados de foco visíveis
- não depender só de cor para status
- labels claros em inputs e ações
- navegação por teclado em filas e cards
- texto explicativo nos scores e estados

### 18.2 Especial atenção

Como a interface usa estados semânticos, cada status deve combinar:

- cor
- ícone
- texto

---

## 19. Página-chave recomendada para prototipação primeiro

Se formos prototipar só uma tela primeiro, ela deve ser:

`Nova Produção + etapa de Mídia`

Motivo:

- concentra a proposta do produto
- mostra o valor dos templates fechados
- mostra a distinção entre automático e manual
- mostra o score contextual, que é o coração conceitual da solução

---

## 20. Resumo da proposta de interface

A interface ideal para este sistema deve ser:

- editorial, não burocrática
- bonita, mas disciplinada
- moderna, mas legível
- orientada a confiança operacional
- forte em curadoria de mídia
- clara na transição entre automação e intervenção humana

Em linguagem simples: a interface deve parecer uma central de produção audiovisual inteligente, e não um painel administrativo genérico nem um editor criativo livre.

