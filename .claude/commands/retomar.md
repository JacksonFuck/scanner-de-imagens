---
description: Carrega contexto do vault e do graph para retomar de onde parou
allowed-tools: Read, Bash, Glob, PowerShell
---

# /retomar

Você acabou de ser invocado num projeto que tem memória persistente em `vault/` e (possivelmente) um knowledge graph em `graphify-out/`. Antes de responder qualquer outra coisa, **carregue o contexto** seguindo estes passos.

## Passos

1. **Listar os 3 últimos session logs** em `vault/logs/`:
   - Use Glob: `vault/logs/*.md`
   - Pegue os 3 mais recentes (por nome — formato `YYYY-MM-DD-*.md`)
   - Leia cada um com Read

2. **Ler o log de decisões**:
   - Read `vault/projeto/decisoes.md`

3. **Ler arquitetura atual**:
   - Read `vault/projeto/arquitetura.md`

4. **Verificar se o Graphify já existe**:
   - Glob: `graphify-out/GRAPH_REPORT.md`
   - Se existir, leia — contém estrutura do código atual
   - Se não existir, anote: "Graphify ainda não rodou (provavelmente sem código-fonte ainda)"

5. **Verificar git status** (se for repo git):
   - Bash: `git status --short` e `git log --oneline -5` (com `cd` se necessário)
   - Capture a branch atual e mudanças não-commitadas

## Output esperado

Imprima um resumo estruturado em português:

```
## Estado atual

**Branch**: <nome>
**Última sessão**: <data do log mais recente>

### O que foi feito recentemente
- <bullet 1>
- <bullet 2>

### Decisões em aberto
- <pendência 1>
- <pendência 2>

### Próximos passos sugeridos
- <bullet>
- <bullet>

### Arquivos-chave para esta sessão
- <path>
- <path>
```

## Regras

- **Não execute código nem modifique arquivos** durante o `/retomar` — é leitura apenas.
- Se algum dos arquivos não existir, prossiga normalmente e mencione no resumo.
- Mantenha o resumo abaixo de **400 palavras**.
- Se houver muitos logs/decisões, priorize os 5 itens mais relevantes.
