---
description: Cria session log no vault/logs/ resumindo o que foi feito nesta sessão
allowed-tools: Read, Write, Bash, PowerShell, Glob
argument-hint: [slug-curto-opcional]
---

# /salvar

Crie um session log em `vault/logs/` documentando o trabalho desta sessão. O argumento opcional `$ARGUMENTS` é um slug curto descritivo (kebab-case). Se não houver argumento, gere um a partir do que foi feito.

## Passos

1. **Determinar a data**: use a data de hoje em formato `YYYY-MM-DD`.
   - PowerShell: `Get-Date -Format 'yyyy-MM-dd'`

2. **Determinar o slug**:
   - Se `$ARGUMENTS` foi passado, use-o (validar kebab-case).
   - Senão, gere a partir do tema principal da sessão (ex.: `setup-vault-inicial`, `fix-docling-tabela`).

3. **Coletar evidências**:
   - `git status --short` e `git diff --stat HEAD` para listar arquivos modificados
   - Quais notas no `vault/` foram criadas/alteradas (Glob com filtro por `LastWriteTime > início da sessão`)
   - Quais decisões foram tomadas (você sabe pela conversa)

4. **Criar o arquivo** `vault/logs/{YYYY-MM-DD}-{slug}.md` com este conteúdo:

```markdown
---
title: {YYYY-MM-DD} — {Título humano}
tags: [log, sessao]
created: {YYYY-MM-DD}
updated: {YYYY-MM-DD}
status: closed
type: log
session_duration: {estimativa em minutos, opcional}
---

# {YYYY-MM-DD} — {Título humano}

## Objetivo da sessão

> O que o usuário pediu / problema enfrentado.

## O que foi feito

- {bullet}
- {bullet}

## Decisões tomadas

- **{Decisão 1}**: motivo. Registrada em [[../projeto/decisoes#{anchor}]].
- **{Decisão 2}**: motivo.

## Arquivos modificados

- `path/relativo/arquivo.py`
- [[arquivo-no-vault]]

## Pendências / próximos passos

- [ ] {pendência 1}
- [ ] {pendência 2}

## Links

- [[../projeto/decisoes]]
- [[../projeto/arquitetura]]
- [[ ]]

## Trecho de comando útil

> Se houver um comando ou snippet que vale guardar para a próxima sessão.

```bash
{comando}
```
```

5. **Sugerir commit** (não executar — usuário decide):
   ```
   Sugestão de commit:
     git add .
     git commit -m "docs(vault): session log {YYYY-MM-DD} — {slug}"
   ```

## Regras

- **Use wikilinks** para qualquer nota referenciada (`[[arquivo]]`, não `[texto](arquivo.md)`).
- **Não invente** — se algo não foi feito ou não foi decidido, omita ou marque como TODO.
- Mantenha o log enxuto: 1 sessão = 1 arquivo. Se a sessão tiver múltiplos temas, separe em logs distintos.
- **Não delete logs antigos** durante o `/salvar`.
- Se já existir um log com o mesmo nome (mesma data + slug), pergunte antes de sobrescrever — sugira `-2`, `-3` no slug.
