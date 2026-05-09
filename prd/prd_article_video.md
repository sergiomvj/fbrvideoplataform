# PRD — Motor Editorial de Vídeos Templated

> Reformulado a partir de `conceito_geral_article_video.md`  
> Status: Draft alinhado ao conceito  
> Objetivo: descrever o produto, seu recorte inicial e os requisitos que deverão orientar a solução

---

## 1. Propósito do produto

O produto existe para transformar conteúdo editorial em vídeos padronizados com rapidez, coerência contextual e controle operacional.

O sistema não nasce como uma plataforma criativa aberta. Ele nasce como um motor editorial controlado, baseado em templates fechados, capaz de operar em fluxo quase automático sem comprometer aderência entre texto, contexto, mídia e composição final.

Seu papel principal é estruturar e montar vídeos a partir de insumos editoriais, usando automação apenas quando a confiança contextual for suficientemente alta.

---

## 2. Problema que o produto resolve

As redações e equipes de conteúdo enfrentam uma combinação recorrente de dificuldades:

- transformar conteúdo textual em vídeo exige tempo e trabalho manual
- a busca de imagens e vídeos de apoio costuma gerar material genérico ou incoerente
- a repetição visual reduz atratividade e diferenciação entre peças
- processos pouco controlados geram especificações inconsistentes e fluxos difíceis de operar
- a ausência de critérios claros de confiança faz com que a automação produza resultados inseguros

O produto deve resolver isso oferecendo uma linha de produção audiovisual disciplinada, com poucos formatos iniciais, validação contextual forte e possibilidade de intervenção humana nos pontos certos.

---

## 3. Definição do produto

O produto é um **motor proprietário de composição editorial de vídeos** com:

- templates fechados
- duas formas de operação
- sistema de aderência contextual para mídia
- montagem controlada
- integração com motor externo de render, inicialmente admissível via provedor como HeyGen

O valor do sistema está na inteligência editorial e estrutural, e não apenas na etapa final de renderização.

---

## 4. Princípios de produto

Os princípios abaixo são obrigatórios para qualquer evolução do produto:

1. O sistema deve privilegiar coerência sobre flexibilidade irrestrita.
2. A automação só deve ocorrer quando houver confiança contextual alta.
3. Todo resultado deve respeitar as regras do template escolhido.
4. A mídia visual não pode ser escolhida por similaridade rasa de palavras-chave.
5. O fluxo manual deve existir como modo legítimo de produção, não como exceção improvisada.
6. O sistema deve impedir que camadas diferentes passem a decidir além do seu papel.
7. O MVP deve restringir formatos e possibilidades para maximizar consistência.

---

## 5. Usuários e papéis

### 5.1 Operador editorial

Responsável por:

- iniciar o fluxo
- escolher template e variação quando aplicável
- revisar candidatos de mídia quando o score não permitir automação total
- usar o modo manual quando necessário

### 5.2 Redação ou empresa cliente

Responsável por:

- definir identidade editorial e institucional
- aprovar padrões de template
- fornecer ativos próprios quando o fluxo manual for usado

### 5.3 Sistema

Responsável por:

- estruturar o conteúdo no template
- produzir briefs visuais por cena
- buscar ou receber ativos
- medir aderência contextual
- decidir entre aprovar, escalar ou retrabalhar
- montar o vídeo de forma consistente

---

## 6. Produtos iniciais

O produto começa com dois templates fechados.

### 6.1 Template A — Presenter Short

Descrição:

- vídeo curto com avatar apresentando o texto
- fundo institucional da redação ou empresa
- uso prioritário para peças rápidas e objetivas

Regras:

- duração máxima: `60s`
- formato: `9:16`
- resolução: `HD`
- 3 variações: `1`, `2`, `3`

Casos de uso:

- notícias curtas
- chamadas editoriais
- resumos
- vídeos de produção rápida

### 6.2 Template B — VideoDoc Narrated

Descrição:

- vídeo mais longo com narração e/ou apresentador
- uso de imagens e vídeos de apoio
- foco em explicação e contextualização

Regras:

- duração máxima: `180s`
- formato: `16:9`
- resolução: `2K`
- 3 variações: `1`, `2`, `3`

Casos de uso:

- videodocs curtos
- conteúdo explicativo
- reportagens contextualizadas
- narrativas com maior densidade visual

### 6.3 Variações visuais

As variações `1`, `2` e `3` existem para reduzir repetição visual e evitar que a produção fique excessivamente homogênea.

As variações:

- não criam novos templates
- não mudam a natureza do produto audiovisual
- devem representar diferenças controladas de composição

Exemplos possíveis de variação:

- abertura
- enquadramento
- hierarquia visual
- ritmo de apresentação
- tratamento institucional

---

## 7. Modos de operação

### 7.1 Fluxo automático assistido

Fluxo voltado para escala com segurança.

O sistema:

1. recebe o conteúdo
2. enquadra no template
3. estrutura a peça
4. define necessidades visuais por cena
5. busca ou seleciona ativos candidatos
6. mede aderência contextual
7. aprova automaticamente apenas quando a confiança for alta
8. envia para revisão humana quando houver plausibilidade sem confiança suficiente
9. monta o vídeo e prepara o job de render

### 7.2 Fluxo manual guiado

Fluxo voltado para controle editorial ampliado.

O usuário participa em uma fase pré-fluxo e pode informar:

- texto base, artigo ou roteiro
- template
- variação
- ativos visuais
- associação de ativos por cena
- elementos obrigatórios
- elementos proibidos

Depois disso, o sistema monta a peça no template escolhido sem reinventar a estrutura.

### 7.3 Quando usar o fluxo manual

O fluxo manual deve ser prioritariamente usado quando houver:

- tema sensível
- baixa qualidade dos candidatos automáticos
- necessidade de usar acervo próprio
- exigência de controle fino da narrativa visual
- contexto em que a automação não possa operar com segurança suficiente

---

## 8. Fluxo funcional do produto

### 8.1 Entrada

O sistema deve aceitar, conforme evolução do produto:

- artigo
- texto base
- roteiro
- insumos visuais manuais no modo guiado

### 8.2 Estruturação editorial

O sistema deve transformar a entrada em uma estrutura compatível com o template, preservando coerência entre:

- objetivo editorial
- duração
- formato
- cenas ou blocos
- tipo de apoio visual necessário

### 8.3 Brief visual por cena

Cada cena ou bloco deve produzir um brief visual estruturado contendo:

- tema
- função visual
- assunto visível desejado
- contexto geográfico/cultural
- época ou contemporaneidade
- tom editorial
- nível de literalidade
- permitidos
- proibidos
- tipo preferido de ativo

### 8.4 Obtenção de mídia

Os ativos podem vir de:

- busca automática
- acervo informado manualmente
- seleção manual em fase pré-fluxo

### 8.5 Verificação de aderência contextual

Todo ativo obtido automaticamente deve ser avaliado antes de entrar na peça.

O sistema deve medir aderência com base em critérios como:

- relevância temática
- aderência à cena
- coerência geográfica/cultural
- coerência temporal
- coerência editorial
- adequação visual
- ausência de conflitos

### 8.6 Política de decisão por score

- `90–100%`: aprovação automática
- `60–89%`: análise humana
- `<60%`: rejeição automática com nova tentativa de obtenção

### 8.7 Regra para scores abaixo de 60%

Se o score for inferior a `60%`, o ativo não deve ir diretamente para revisão humana.

O sistema deve:

1. identificar a causa principal da baixa aderência
2. ajustar o brief e/ou a estratégia de busca
3. gerar nova consulta ou prompt
4. obter novos candidatos
5. reavaliar

Se, após tentativas automáticas, o sistema continuar sem obter candidatos acima de `60%`, o caso deve ser tratado como falha estrutural de obtenção.

### 8.8 Montagem final

A montagem deve:

- respeitar o template
- respeitar a variação escolhida
- respeitar os limites de duração e formato
- respeitar os ativos aprovados
- preparar a saída para renderização

---

## 9. Requisitos funcionais

### 9.1 Núcleo de operação

- `FR-001`: o sistema deve suportar o template `Presenter Short`.
- `FR-002`: o sistema deve suportar o template `VideoDoc Narrated`.
- `FR-003`: cada template deve possuir as variações `1`, `2` e `3`.
- `FR-004`: o sistema deve operar em modo automático assistido.
- `FR-005`: o sistema deve operar em modo manual guiado.
- `FR-006`: o sistema deve permitir seleção explícita do template.
- `FR-007`: o sistema deve permitir seleção explícita da variação.

### 9.2 Estruturação e montagem

- `FR-008`: o sistema deve transformar a entrada em estrutura compatível com o template.
- `FR-009`: o sistema deve gerar briefs visuais por cena ou bloco.
- `FR-010`: o sistema deve montar a peça final respeitando a estrutura do template.
- `FR-011`: o sistema não deve permitir que a montagem final desrespeite os limites do template.

### 9.3 Subsistema de mídia

- `FR-012`: o sistema deve permitir obtenção automática de ativos visuais.
- `FR-013`: o sistema deve permitir fornecimento manual de ativos no fluxo guiado.
- `FR-014`: o sistema deve avaliar a aderência contextual de ativos automáticos.
- `FR-015`: o sistema deve classificar ativos em aprovação automática, revisão humana ou rejeição com retrabalho.
- `FR-016`: o sistema deve reprocessar automaticamente buscas abaixo de `60%`.
- `FR-017`: o sistema deve encaminhar para humano apenas candidatos plausíveis.

### 9.4 Controle editorial

- `FR-018`: o sistema deve preservar coerência entre texto, mídia e template.
- `FR-019`: o sistema deve permitir marcação de elementos obrigatórios e proibidos no modo manual.
- `FR-020`: o sistema deve registrar a decisão operacional tomada para cada ativo aprovado, rejeitado ou escalado.

### 9.5 Render e saída

- `FR-021`: o sistema deve produzir uma saída pronta para renderização.
- `FR-022`: o sistema deve ser compatível com integração inicial com provedor externo de render.
- `FR-023`: o sistema deve distinguir claramente a inteligência proprietária da camada de render externo.

---

## 10. Requisitos não funcionais

- `NFR-001`: o produto deve priorizar consistência editorial sobre variedade prematura.
- `NFR-002`: o produto deve operar com comportamento previsível e auditável.
- `NFR-003`: toda decisão automática deve ser explicável em nível operacional.
- `NFR-004`: o sistema deve permitir revisão humana sem quebrar o fluxo.
- `NFR-005`: a automação deve ser conservadora em cenários ambíguos.
- `NFR-006`: o sistema deve ser evolutivo sem exigir redefinição completa do conceito base.
- `NFR-007`: o produto deve manter separação clara entre composição editorial e renderização.

---

## 11. Escopo inicial

### 11.1 Incluído

- dois templates fechados
- três variações por template
- fluxo automático assistido
- fluxo manual guiado
- geração de briefs visuais
- mecanismo de score de aderência contextual
- política de aprovação, revisão e retrabalho
- montagem final orientada a render externo

### 11.2 Não incluído neste primeiro recorte

- editor livre de vídeo
- quantidade arbitrária de templates
- liberdade irrestrita de composição
- automação total sem controle de confiança
- uso de mídia sem verificação contextual

---

## 12. Critérios de sucesso do produto

O produto estará cumprindo bem seu papel quando:

- produzir vídeos consistentes dentro dos dois templates definidos
- reduzir dependência de montagem manual repetitiva
- diminuir incidência de mídia incoerente com a narrativa
- operar com automação segura para casos de alta confiança
- escalar para revisão humana apenas onde isso agrega valor real

---

## 13. Critérios de aceite do recorte conceitual

- `CA-001`: o PRD deve refletir fielmente o `Conceito Geral`.
- `CA-002`: os dois templates iniciais devem estar claramente definidos.
- `CA-003`: os dois modos de operação devem estar claramente definidos.
- `CA-004`: a política de score contextual deve estar explicitamente incorporada ao produto.
- `CA-005`: o modo manual deve estar tratado como parte estrutural do sistema.
- `CA-006`: o documento não deve impor decisões técnicas prematuras que ainda não estejam fechadas.

---

## 14. Dependências para a próxima etapa

Este PRD deve servir como base para:

- reformulação da SPEC
- delimitação do MVP executável
- posterior decisão arquitetural
- futura decomposição em épicos e stories

Qualquer SPEC futura deve derivar deste documento e não contradizê-lo.
