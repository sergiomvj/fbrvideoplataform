# Conceito Geral — Motor Editorial de Vídeos Templated

> Base conceitual para reformulação do PRD e da SPEC  
> Status: Draft de alinhamento conceitual  
> Objetivo: consolidar as verdades fundamentais do sistema antes de novas especificações

---

## 1. Propósito deste documento

Este documento existe para fixar o conceito real do sistema antes de qualquer detalhamento de produto, arquitetura ou implementação.

As tentativas anteriores falharam porque diferentes partes do sistema foram descritas com lógicas incompatíveis entre si, gerando documentos volumosos, pouco coerentes e difíceis de transformar em solução prática.

O objetivo aqui não é descrever tecnologia, endpoints, banco de dados ou estrutura de código. O objetivo é estabelecer uma base conceitual única, rígida e consistente, da qual o PRD e a SPEC deverão derivar depois.

---

## 2. Definição do sistema

O sistema é um **motor proprietário de composição editorial de vídeos** baseado em **templates fechados**.

Ele transforma conteúdo editorial em vídeos padronizados, contextualmente coerentes e prontos para renderização, utilizando:

- inteligência proprietária para estruturar narrativa e composição
- regras rígidas de template
- controle de aderência entre texto, mídia e contexto
- automação com revisão humana quando a confiança não for suficiente

O sistema **não deve nascer como uma plataforma criativa aberta**.

Ele deve nascer como um sistema controlado, previsível e orientado à consistência operacional.

---

## 3. Onde está o valor principal

O valor principal do sistema não está, inicialmente, no render do vídeo.

O valor principal está em:

- enquadrar corretamente o conteúdo editorial em formatos audiovisuais fechados
- traduzir intenção editorial em estrutura visual utilizável
- garantir aderência contextual entre roteiro e material visual
- automatizar com segurança sem permitir deriva de qualidade
- manter um fluxo produtivo que possa escalar sem virar ruído operacional

O render final pode inicialmente ser executado por um provedor externo, como a HeyGen, desde que a inteligência central do sistema permaneça proprietária.

---

## 4. Princípio estrutural

O sistema não deve ser pensado como “gerador genérico de vídeos”.

Ele deve ser pensado como um **compositor editorial controlado**.

Isso significa que:

- o conteúdo de entrada não define livremente a forma final
- a IA não decide formatos por conta própria
- a mídia visual não entra por similaridade rasa de palavra-chave
- o template não inventa narrativa fora de suas regras
- o render é executor, não autor

Cada camada do sistema deve saber com precisão:

- o que recebe
- o que pode decidir
- o que não pode decidir
- o que entrega para a próxima etapa

Esse princípio é obrigatório para evitar novas inconsistências entre módulos.

---

## 5. Produtos iniciais do sistema

O sistema começa com apenas **dois produtos audiovisuais fechados**.

Essa restrição é deliberada e estratégica.

O objetivo inicial é viabilizar um fluxo confiável, repetível e comercialmente útil, sem abrir o sistema cedo demais.

### 5.1 Template 1 — Presenter Short

Características:

- duração máxima de `60 segundos`
- formato `9:16`
- resolução `HD`
- avatar apresentando o texto
- fundo institucional da redação/empresa
- foco em consumo rápido
- 3 variações visuais: `1`, `2` e `3`

Objetivo:

- notícias curtas
- chamadas editoriais
- resumos rápidos
- vídeos com alta velocidade de produção

### 5.2 Template 2 — VideoDoc Narrated

Características:

- duração máxima de `180 segundos`
- formato `16:9`
- resolução `2K`
- apresentador e/ou narração com apoio de imagens e vídeos
- estrutura mais explicativa
- 3 variações visuais: `1`, `2` e `3`

Objetivo:

- vídeos mais longos
- explicações contextuais
- conteúdos de reportagem
- peças com maior densidade narrativa

### 5.3 Natureza das variações 1, 2 e 3

As variações existem para reduzir repetição visual e evitar que os vídeos fiquem excessivamente parecidos, especialmente nas thumbs e nas primeiras impressões.

As variações não devem criar novos templates.

Elas devem atuar como diferenças controladas dentro do mesmo template, como por exemplo:

- composição de abertura
- enquadramento visual
- ritmo de apresentação
- ordem de blocos visuais permitidos
- tratamento visual institucional

As variações devem ser previsíveis e controláveis.

---

## 6. Dois modos de operação

O sistema deve suportar **dois modos legítimos de produção**.

Ambos usam os mesmos templates e a mesma lógica final de montagem.

O que muda é a forma de obtenção e controle dos insumos.

### 6.1 Fluxo automático assistido

Neste modo, o sistema:

- recebe o conteúdo de entrada
- adapta o conteúdo ao template escolhido
- estrutura narrativa e elementos visuais
- busca ou seleciona mídia de apoio
- avalia aderência contextual
- aprova automaticamente apenas quando houver confiança alta
- encaminha para revisão humana quando necessário
- monta o vídeo no template
- prepara e/ou envia o job para renderização

Esse fluxo existe para ganho de escala com segurança.

### 6.2 Fluxo manual guiado

Neste modo, o usuário participa antes da montagem final.

Ele informa ou aponta os elementos do vídeo em uma fase pré-fluxo e o sistema usa esses elementos para compor o vídeo no template escolhido.

Esse modo existe para:

- temas sensíveis
- baixa confiança da busca automática
- uso de acervo próprio
- controle editorial mais fino
- situações em que a redação já possui os ativos corretos

O fluxo manual não elimina o template.

Ele apenas substitui ou reduz a dependência da seleção automática de elementos.

---

## 7. Fase pré-fluxo do modo manual

No modo manual, existe uma etapa anterior à montagem em que o usuário pode indicar os insumos essenciais da peça.

Esses insumos podem incluir:

- texto base
- artigo
- roteiro
- template desejado
- variação `1`, `2` ou `3`
- avatar/apresentador aplicável
- imagens selecionadas
- vídeos selecionados
- associação de ativos por cena ou por bloco
- elementos obrigatórios
- elementos proibidos

Após essa etapa, o sistema deve montar o vídeo respeitando as regras estruturais do template, sem reinventar a peça.

---

## 8. Regra central de coerência

O sistema deve garantir que **texto, contexto, mídia e template permaneçam coerentes entre si**.

Essa é a regra-mãe do projeto.

Sempre que uma dessas camadas se desconectar das demais, a qualidade editorial do resultado se deteriora.

Por isso:

- o roteiro não pode pedir uma visualidade que o template não suporta
- a mídia não pode ilustrar algo que contradiz a cena
- o template não pode forçar uma estrutura incompatível com o conteúdo
- a automação não pode avançar se a aderência contextual for insuficiente

---

## 9. Subsistema de mídia

O subsistema de mídia é uma parte crítica do conceito e não pode ser tratado como detalhe secundário.

O material visual de apoio não deve ser escolhido por “palavra-chave parecida”.

Ele deve ser escolhido por **aderência ao contexto da cena**.

### 9.1 O que o sistema busca

O sistema não busca “imagens bonitas”.

Ele busca material visual que cumpra uma função narrativa e editorial.

### 9.2 Funções visuais possíveis

Cada cena deve apontar qual função visual precisa ser atendida.

Funções visuais iniciais:

- `evidencia_literal`
- `contexto_ambiental`
- `cobertura_broll`
- `prova_documental`
- `metafora_controlada` somente quando explicitamente permitida

### 9.3 Brief visual da cena

Antes da busca de imagens ou vídeos, cada cena deve ser traduzida em um **brief visual estruturado**.

Esse brief deve conter, no mínimo:

- tema da cena
- função visual esperada
- assunto visível desejado
- contexto geográfico/cultural
- período ou contemporaneidade
- tom editorial
- nível de literalidade
- elementos permitidos
- elementos proibidos
- tipo preferido de ativo

Sem esse brief, a busca tende a virar aproximação genérica e compromete o sistema inteiro.

---

## 10. Verificação de aderência contextual

Todo ativo de mídia obtido automaticamente deve ser verificado antes de entrar no fluxo.

Essa verificação não deve perguntar apenas se o material “tem a ver” com o assunto em termos vagos.

Ela deve avaliar se o ativo é realmente adequado para a cena e para o vídeo.

### 10.1 Critérios de aderência

O índice de aderência contextual deve considerar, pelo menos:

- relevância temática
- aderência à cena específica
- coerência geográfica/cultural
- coerência temporal
- coerência editorial
- adequação visual/narrativa
- ausência de conflitos ou contradições

### 10.2 Regra de segurança operacional

O sistema deve operar com três faixas de decisão:

- `90–100%`: aprovação automática
- `60–89%`: análise humana
- `<60%`: rejeição automática com nova tentativa de obtenção

### 10.3 Regra obrigatória para índices abaixo de 60%

Materiais com aderência abaixo de `60%` **não devem seguir diretamente para análise humana**.

Antes disso, o sistema deve:

- identificar a causa principal da baixa aderência
- ajustar o brief visual e/ou o padrão de busca
- gerar uma nova consulta/prompt
- obter novos candidatos
- recalcular a aderência

O objetivo é que apenas materiais minimamente plausíveis cheguem à análise humana.

### 10.4 Revisão humana

A revisão humana deve se concentrar em candidatos que já tenham qualidade mínima para avaliação.

Ou seja:

- o humano não deve perder tempo com material obviamente inadequado
- o humano deve atuar onde há plausibilidade, mas ainda não há segurança suficiente para automação total

### 10.5 Casos de falha estrutural

Se após tentativas automáticas o sistema continuar incapaz de obter material com aderência acima de `60%`, isso não deve ser tratado como simples “ausência de revisão”.

Isso caracteriza falha estrutural de obtenção ou inadequação do brief para aquela cena.

Nesses casos, o fluxo deve escalar para intervenção humana em nível mais alto, com revisão da estratégia de mídia.

---

## 11. Limites da automação

O sistema deve ser capaz de operar quase automaticamente, mas nunca de forma irresponsável.

Automação só é válida quando existir alto grau de confiança contextual.

Portanto:

- o sistema não deve improvisar quando não encontrar mídia coerente
- o sistema não deve “forçar aprovação” para manter fluidez
- o sistema deve poder interromper, escalar ou pedir validação
- o sistema deve ser conservador em temas sensíveis ou ambíguos

O objetivo não é automatizar a qualquer custo.

O objetivo é automatizar com segurança editorial.

---

## 12. O que cada camada não pode fazer

Para preservar coerência, algumas fronteiras devem ser rígidas.

### 12.1 O template não pode

- redefinir a linha editorial
- criar formatos fora do seu escopo
- aceitar qualquer estrutura arbitrária de cena

### 12.2 A IA não pode

- inventar fatos
- desrespeitar o template
- decidir livremente formatos não previstos
- criar visuais incompatíveis com o vocabulário permitido

### 12.3 A busca de mídia não pode

- operar por similaridade rasa de keyword
- escolher ativos sem validação contextual
- substituir intenção editorial por estética genérica

### 12.4 O render não pode

- reinterpretar a narrativa
- reestruturar a peça
- se comportar como camada criativa

### 12.5 O fluxo manual não pode

- quebrar as regras do template
- transformar o sistema em editor livre
- introduzir incoerência estrutural só porque os ativos foram escolhidos manualmente

---

## 13. Verdades fundamentais do sistema

As afirmações abaixo devem servir como referência central para PRD e SPEC.

1. O sistema é um motor editorial de composição de vídeos, não um gerador criativo genérico.
2. O sistema começa com dois templates fechados e controlados.
3. A inteligência principal do sistema deve permanecer proprietária, mesmo que o render inicial use terceiros.
4. O valor principal está na estruturação editorial, na coerência contextual e na montagem controlada.
5. Texto, contexto, mídia e template devem permanecer alinhados durante todo o fluxo.
6. A mídia visual só entra no fluxo quando há aderência contextual suficiente.
7. A aprovação automática só pode ocorrer em faixa alta de confiança.
8. Materiais fracos devem ser retrabalhados automaticamente antes de consumir revisão humana.
9. O sistema deve suportar tanto fluxo automático assistido quanto fluxo manual guiado.
10. O fluxo manual existe para ampliar controle sem romper a disciplina estrutural do sistema.
11. Nenhuma camada do sistema deve decidir além do seu papel.
12. Toda futura especificação deve derivar destas verdades e não contradizê-las.

---

## 14. Papel deste documento na próxima etapa

Este documento deve funcionar como **fonte conceitual primária** para:

- reescrever o PRD
- reescrever a SPEC
- delimitar MVP
- avaliar arquitetura
- evitar expansão prematura de escopo

Se um futuro PRD ou SPEC contradizer este documento, a contradição deve ser tratada antes de prosseguir.

O objetivo é impedir que o projeto volte a produzir documentos grandes, sofisticados na aparência, mas incongruentes entre si.

