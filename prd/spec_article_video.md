# SPEC — Motor Editorial de Vídeos Templated

> Reformulada a partir do `Conceito Geral` e do novo `PRD`  
> Status: Draft funcional do sistema  
> Objetivo: detalhar como o sistema deve se comportar sem antecipar decisões arquiteturais ainda não fechadas

---

## 1. Propósito da SPEC

Esta SPEC descreve a estrutura funcional do sistema, seus módulos, contratos conceituais, regras de decisão e limites operacionais.

Ela não deve forçar stack, framework, banco ou infraestrutura como verdade fechada enquanto essas decisões ainda não estiverem formalmente aprovadas.

Seu papel é responder:

- quais são as partes do sistema
- o que cada parte recebe
- o que cada parte pode decidir
- o que cada parte entrega
- como o sistema preserva coerência entre conteúdo, mídia e template

---

## 2. Relação entre os três documentos

### 2.1 Conceito Geral

Define as verdades fundamentais do sistema.

### 2.2 PRD

Define o produto, o recorte inicial, os requisitos e o comportamento esperado do ponto de vista de negócio e operação.

### 2.3 SPEC

Detalha a organização funcional necessária para implementar o produto sem violar o conceito.

Se houver conflito entre estes documentos:

1. o `Conceito Geral` prevalece
2. o `PRD` detalha o produto dentro desse conceito
3. a `SPEC` deve obedecer aos dois anteriores

---

## 3. Visão funcional do sistema

O sistema é um motor de composição audiovisual editorial baseado em templates fechados.

Seu funcionamento de alto nível é:

1. receber conteúdo e intenção de produção
2. enquadrar a peça em um template
3. estruturar o conteúdo em blocos ou cenas
4. definir necessidades visuais por cena
5. obter ou receber ativos visuais
6. medir aderência contextual desses ativos
7. decidir entre aprovar, revisar ou retrabalhar
8. montar a peça no template
9. produzir uma saída pronta para renderização

---

## 4. Templates suportados

### 4.1 Template A — Presenter Short

Contrato funcional:

- vídeo curto
- limite de duração: `60s`
- formato final: `9:16`
- resolução alvo: `HD`
- avatar apresentando o texto
- fundo institucional
- 3 variações visuais

### 4.2 Template B — VideoDoc Narrated

Contrato funcional:

- vídeo mais longo
- limite de duração: `180s`
- formato final: `16:9`
- resolução alvo: `2K`
- narração e/ou apresentador
- suporte a imagens e vídeos de apoio
- 3 variações visuais

### 4.3 Regras dos templates

Todos os templates devem:

- ter limites de duração explícitos
- ter regras próprias de composição
- restringir o que pode ou não ser montado
- aceitar variações apenas dentro do template

Nenhum template pode:

- agir como editor livre
- aceitar qualquer estrutura arbitrária
- redefinir sozinho a linha editorial da peça

---

## 5. Modos de operação

### 5.1 Modo automático assistido

Entrada:

- conteúdo textual
- template
- variação
- contexto editorial necessário

Comportamento:

- o sistema estrutura a peça
- o sistema produz briefs visuais
- o sistema busca ou seleciona ativos automaticamente
- o sistema mede aderência contextual
- o sistema decide se aprova, escala ou retrabalha

Saída:

- composição pronta para render
- ou fila de revisão humana

### 5.2 Modo manual guiado

Entrada:

- conteúdo textual
- template
- variação
- ativos visuais indicados pelo usuário
- restrições e obrigatoriedades

Comportamento:

- o sistema recebe os elementos definidos pelo usuário
- o sistema valida compatibilidade com o template
- o sistema organiza esses elementos na estrutura final

Saída:

- composição pronta para render
- ou indicação de inconsistência estrutural caso os insumos manuais não caibam no template

---

## 6. Módulos funcionais

### 6.1 Módulo de entrada

Responsável por receber:

- artigo
- texto base
- roteiro
- metadados operacionais
- template
- variação
- modo de operação

Não pode:

- decidir sozinho a estrutura final
- ignorar restrições do template

Entrega:

- pacote de entrada normalizado

### 6.2 Módulo de estruturação editorial

Responsável por:

- transformar a entrada em estrutura compatível com o template
- definir cenas ou blocos
- adequar extensão e densidade ao limite do formato

Não pode:

- inventar um template novo
- produzir estrutura incompatível com o template escolhido

Entrega:

- estrutura narrativa base

### 6.3 Módulo de planejamento visual

Responsável por:

- converter cada cena em brief visual
- declarar função visual
- definir o que precisa aparecer
- explicitar permitidos e proibidos

Não pode:

- operar com brief vago
- reduzir a busca a palavras-chave genéricas

Entrega:

- briefs visuais estruturados por cena

### 6.4 Módulo de obtenção de mídia

Responsável por:

- buscar ativos automaticamente
- receber ativos manuais quando fornecidos
- preparar candidatos para avaliação

Não pode:

- aprovar ativos por conta própria
- substituir controle editorial por “melhor esforço”

Entrega:

- lista de candidatos por cena

### 6.5 Módulo de verificação contextual

Responsável por:

- medir aderência contextual dos candidatos automáticos
- explicar os motivos da nota
- orientar decisão operacional

Não pode:

- produzir score opaco
- aprovar automaticamente sem cumprir a política de decisão

Entrega:

- score por ativo
- justificativa
- status operacional

### 6.6 Módulo de decisão operacional

Responsável por aplicar a política:

- `90–100%`: aprovar automaticamente
- `60–89%`: escalar para humano
- `<60%`: rejeitar e reobter

Também deve:

- identificar casos de falha estrutural de obtenção
- impedir que revisão humana receba candidatos claramente inadequados

Entrega:

- decisão final por ativo ou por cena

### 6.7 Módulo de montagem

Responsável por:

- aplicar a estrutura narrativa ao template
- inserir os ativos aprovados
- respeitar a variação escolhida
- gerar composição final pronta para render

Não pode:

- alterar regras do template
- inserir ativos não aprovados

Entrega:

- composição final estruturada

### 6.8 Módulo de saída para render

Responsável por:

- transformar a composição final em payload executável
- preparar integração com provedor externo de render

Não pode:

- reinterpretar a peça
- modificar estrutura editorial

Entrega:

- payload pronto para execução

---

## 7. Contratos conceituais de dados

Os contratos abaixo não definem tecnologia. Eles definem o mínimo que cada etapa precisa transportar.

### 7.1 Pacote de entrada normalizado

Campos conceituais mínimos:

- `modo_operacao`
- `tipo_entrada`
- `conteudo_base`
- `template_id`
- `variacao_id`
- `contexto_editorial`
- `restricoes`

### 7.2 Estrutura narrativa base

Campos conceituais mínimos:

- `objetivo_da_peca`
- `duracao_alvo`
- `template_id`
- `variacao_id`
- `blocos_ou_cenas`

Cada bloco ou cena deve conter, no mínimo:

- `id`
- `papel_narrativo`
- `texto_ou_narracao`
- `duracao_estimada`

### 7.3 Brief visual da cena

Campos conceituais mínimos:

- `cena_id`
- `tema`
- `funcao_visual`
- `assunto_visivel`
- `contexto_geografico_cultural`
- `periodo`
- `tom_editorial`
- `nivel_literalidade`
- `permitidos`
- `proibidos`
- `tipo_ativo_preferido`

### 7.4 Candidato de mídia

Campos conceituais mínimos:

- `asset_id`
- `origem`
- `tipo`
- `referencia`
- `cena_id`

### 7.5 Resultado de verificação contextual

Campos conceituais mínimos:

- `asset_id`
- `cena_id`
- `score_aderencia`
- `justificativa_curta`
- `falhas_detectadas`
- `status_decisao`

### 7.6 Composição final

Campos conceituais mínimos:

- `template_id`
- `variacao_id`
- `timeline_estruturada`
- `ativos_aprovados`
- `narracao_final`
- `metadata_de_render`

---

## 8. Subsistema de mídia

### 8.1 Objetivo

Garantir que os ativos visuais utilizados em cada cena sejam coerentes com o contexto narrativo e editorial.

### 8.2 Regra de entrada

Ativos automáticos só podem entrar no fluxo produtivo após validação de aderência contextual.

### 8.3 Funções visuais suportadas

O sistema deve trabalhar inicialmente com:

- `evidencia_literal`
- `contexto_ambiental`
- `cobertura_broll`
- `prova_documental`
- `metafora_controlada` quando explicitamente permitida

### 8.4 Heurística de busca

A estratégia de busca deve partir do brief visual da cena, e não do texto bruto da narração.

Isso significa que a consulta precisa refletir:

- o que deve ser mostrado
- em que contexto
- com que grau de literalidade
- com quais restrições

### 8.5 Diagnóstico de baixa aderência

Quando um ativo obtiver score abaixo de `60%`, o sistema deve tentar identificar a origem principal da falha, por exemplo:

- tema genérico demais
- contexto geográfico errado
- época incompatível
- literalidade insuficiente
- tom visual inadequado
- contradição factual

Esse diagnóstico deve alimentar a próxima tentativa de obtenção.

### 8.6 Limite operacional

Se o sistema seguir sem atingir o patamar mínimo de plausibilidade após tentativas automáticas, o caso deve ser marcado como falha estrutural de obtenção e escalado para intervenção adequada.

---

## 9. Política de aderência contextual

### 9.1 Escala de decisão

- `90–100`: uso automático permitido
- `60–89`: uso condicionado à análise humana
- `<60`: uso proibido, com regeneração obrigatória da busca

### 9.2 Critérios mínimos do score

O score deve considerar:

- relevância temática
- aderência à cena
- coerência geográfica/cultural
- coerência temporal
- coerência editorial
- adequação visual
- ausência de conflitos

### 9.3 Regra de auditabilidade

Toda nota precisa ser acompanhada de justificativa operacional resumida.

O sistema não deve operar com score não explicável.

### 9.4 Regra de segurança

Em caso de ambiguidade relevante, o sistema deve preferir revisão humana à aprovação automática.

---

## 10. Regras de integridade do sistema

### 10.1 Integridade narrativa

A narrativa final deve permanecer compatível com:

- o template
- a duração
- a função de cada cena
- o tipo de vídeo pretendido

### 10.2 Integridade visual

Cada ativo usado deve:

- servir à cena
- não contradizer o conteúdo
- não quebrar o tom da peça

### 10.3 Integridade estrutural

O modo manual não pode quebrar o template.

O modo automático não pode forçar material inadequado para manter fluidez.

### 10.4 Integridade de fronteiras

Cada módulo deve decidir apenas dentro de seu escopo.

---

## 11. Casos de uso prioritários

### 11.1 Caso de uso A — Presenter Short em automático

Fluxo:

1. operador informa conteúdo
2. escolhe `Presenter Short`
3. escolhe variação
4. sistema estrutura a peça
5. sistema seleciona ou valida os elementos necessários
6. composição é montada
7. payload é gerado para render

### 11.2 Caso de uso B — VideoDoc com curadoria humana

Fluxo:

1. operador informa conteúdo
2. escolhe `VideoDoc Narrated`
3. sistema gera briefs visuais
4. busca automática retorna candidatos mistos
5. ativos entre `60–89` vão para humano
6. humano aprova candidatos plausíveis
7. sistema monta a peça e gera payload

### 11.3 Caso de uso C — Fluxo manual guiado

Fluxo:

1. operador escolhe template e variação
2. operador informa ativos manualmente
3. sistema valida compatibilidade estrutural
4. sistema monta o vídeo sem redefinir a estrutura
5. payload final é preparado

---

## 12. Saídas esperadas do sistema

O sistema deve ser capaz de produzir:

- composição narrativa estruturada
- conjunto de ativos aprovados
- rastreabilidade da decisão de mídia
- payload final para render
- sinalização explícita de revisão humana ou falha estrutural quando aplicável

---

## 13. Itens deliberadamente não fechados nesta SPEC

Para evitar nova incongruência documental, esta SPEC não fecha ainda:

- stack de backend
- framework de API
- banco de dados
- mecanismo de filas
- forma exata da integração externa
- escolha definitiva de fornecedor de mídia
- algoritmo final de score e seus pesos

Esses pontos deverão ser tratados em etapa arquitetural posterior, sempre respeitando este comportamento funcional.

---

## 14. Critérios de conformidade da implementação futura

Uma implementação futura só será considerada aderente a esta SPEC se:

- respeitar os dois templates iniciais
- respeitar os dois modos de operação
- implementar o subsistema de mídia com validação contextual
- aplicar corretamente a política `90–100`, `60–89`, `<60`
- impedir que o fluxo manual viole a estrutura do template
- preservar fronteiras claras entre módulos
- manter separação entre inteligência editorial e render externo

---

## 15. Próximos artefatos derivados

Esta SPEC deve servir de base para:

- discussão arquitetural formal
- definição do MVP executável
- decomposição em épicos
- criação posterior de stories
- desenho de contratos técnicos reais

Nenhum desses artefatos deve contrariar o `Conceito Geral`, o `PRD` ou esta `SPEC`.
