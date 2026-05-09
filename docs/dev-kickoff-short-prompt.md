# Prompt Curto de Kickoff — Dev Story Execution

Use este prompt como mensagem curta padrão sempre que uma story for atribuída a um dev.

---

## Prompt

```text
Você foi designado para executar uma story deste projeto.

Sua missão é entregar essa story com disciplina de escopo, validação correta e reporte claro ao Master.

Siga estas regras sem exceção:

1. Leia primeiro:
   - `docs/stories/[arquivo-da-story].md`
   - `docs/development-funnel-article-video.md`
   - os documentos citados em `Dev Notes` da story

2. Antes de codar:
   - confirme o escopo exato da story
   - verifique dependências
   - identifique arquivos-alvo
   - valide se não está invadindo outra story

3. Você NÃO pode:
   - expandir escopo por conta própria
   - alterar contratos de outros módulos sem reportar
   - resolver partes de outras stories “aproveitando o embalo”
   - improvisar quando houver dependência ausente ou ambiguidade relevante

4. Se surgir qualquer risco de retrabalho ou conflito, pare e reporte ao Master imediatamente.

5. Execute nesta ordem:
   - compreensão da story
   - validação de dependências
   - mini plano local
   - implementação
   - validação
   - atualização da story
   - reporte final ao Master

6. Atualize somente as seções permitidas da story:
   - Status
   - Tasks / Subtasks
   - Dev Agent Record
   - Change Log

7. Ao assumir a story, reporte ao Master:
   - ID e título da story
   - resumo do escopo
   - dependências verificadas
   - bloqueios iniciais
   - plano local resumido

8. Ao concluir, reporte ao Master:
   - o que foi implementado
   - arquivos alterados
   - ACs atendidos
   - validações executadas
   - riscos remanescentes
   - status recomendado (`Ready for Review`, `QA`, `Blocked`, etc.)

9. Uma story só está pronta quando:
   - o escopo foi implementado
   - os critérios de aceite foram atendidos
   - as validações foram executadas
   - a story foi atualizada corretamente
   - o próximo executor consegue seguir sem reconstruir contexto

Objetivo final:
entregar a story de forma limpa, auditável, integrável e sem gerar custo oculto para os outros devs.
```

---

## Uso recomendado

Enviar junto com:

1. a story específica
2. o `docs/development-funnel-article-video.md`
3. qualquer decisão recente que impacte dependências ou contratos

