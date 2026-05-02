# Plano — Setup Obsidian + Graphify + Pipeline de Chats para "Scanner de Imagens"

## Context

O projeto **"Scanner de Imagens"** está em estado greenfield (apenas `CLAUDE.md` de regras context-mode e pasta `reports/`). O objetivo é construir um app que recebe **fotografias de páginas de livros/artigos** e gera **Markdown estruturado** com possibilidade de export para **DOCX**, preservando imagens e qualidade.

Antes de começar a codificar a aplicação, vamos montar a infraestrutura de **memória persistente e knowledge graph** descrita no guia que você compartilhou — adaptada para Windows + vault local. Isso resolve dois problemas:

1. **Amnésia entre sessões** do Claude Code (perde contexto a cada conversa nova).
2. **Releitura desnecessária do codebase** (consome ~20k tokens só para se orientar).

A escolha foi **vault local dentro do projeto** (`Scanner de imagens\vault\`) — o vault viaja com o repo, sem fragmentação cross-projeto.

### Decisão técnica adicional sobre a stack do app

A regra global em `~/.claude/rules/pdf-extraction-default.md` define **opendataloader-pdf** como default — mas é **PDF-only**. Como o input são fotos JPG/PNG de páginas:

| Estratégia | Prós | Contras |
|-----------|------|---------|
| **Docling** (recomendado) | Aceita JPG/PNG direto, OCR + layout, export Markdown nativo | Requer Python + GPU opcional |
| Pillow → PDF → OpenDataloader | Respeita regra global do user | Pipeline em 2 etapas, perda de qualidade no merge |
| Híbrido (Docling primário, OpenDataloader fallback) | Flexível | Mais complexo |

**Decisão proposta:** Docling primário para fotos. Documentar exceção à regra global no `CLAUDE.md` do projeto. **Confirmar antes de começar a codificar a aplicação** (este plano cobre apenas a infraestrutura).

---

## Arquitetura Final do Setup

```
C:\Users\jacks\OneDrive\2º Cérebro\Scanner de imagens\
├── CLAUDE.md                       # MERGE: context-mode + Context Navigation + Zettelkasten
├── reports/                        # já existe
├── vault/                          # NOVO — Obsidian vault local
│   ├── .obsidian/                  # criado pelo Obsidian ao abrir
│   ├── CLAUDE.md                   # instruções Zettelkasten para o vault
│   ├── permanent/                  # notas atômicas consolidadas
│   ├── inbox/                      # captura bruta
│   ├── fleeting/                   # rascunhos
│   ├── templates/
│   │   └── nota-padrao.md
│   ├── logs/                       # session logs (/salvar)
│   ├── references/
│   ├── projeto/                    # MOCs do Scanner de Imagens
│   │   ├── arquitetura.md
│   │   ├── decisoes.md
│   │   └── convencoes.md
│   ├── pipeline/
│   ├── dados/
│   ├── features/
│   ├── chats/
│   │   ├── code/                   # imports do Claude Code
│   │   └── web/                    # imports do Claude Web
│   └── graphify/                   # notas geradas pelo Graphify (após existir código)
├── graphify-out/                   # NOVO — só após existir código-fonte
│   ├── graph.json                  # consultado pelo Claude Code
│   ├── graph.html
│   ├── GRAPH_REPORT.md
│   ├── wiki/
│   └── cache/
├── scripts/                        # NOVO — automação local (versionado no git)
│   ├── claude_to_obsidian.py
│   └── sync_claude_obsidian.ps1    # PowerShell (Windows-native, não bash)
├── claude-exports/                 # staging area (gitignored)
│   ├── code/
│   └── web/
└── .claude/                        # NOVO — comandos custom
    └── commands/
        ├── retomar.md
        └── salvar.md
```

---

## Fase 1 — Estrutura do Vault + CLAUDE.md Global

### 1.1. Criar estrutura de pastas

PowerShell (uma única chamada):

```powershell
$base = "C:\Users\jacks\OneDrive\2º Cérebro\Scanner de imagens\vault"
$dirs = @(
  "permanent","inbox","fleeting","templates","logs","references",
  "projeto","pipeline","dados","features",
  "chats\code","chats\web","graphify"
)
$dirs | ForEach-Object { New-Item -ItemType Directory -Force -Path "$base\$_" | Out-Null }
```

### 1.2. Criar `vault/CLAUDE.md`

Instruções Zettelkasten (wikilinks, frontmatter, atomicidade, regras `/retomar` e `/salvar`). Adapta o template do guia para o contexto deste único projeto.

### 1.3. Criar `vault/templates/nota-padrao.md`

Template com frontmatter YAML padrão (`title`, `tags`, `created`, `updated`, `status`, `type`).

### 1.4. Criar MOCs iniciais do projeto

- `vault/projeto/arquitetura.md` — placeholder com seção "Decisão: Docling vs OpenDataloader"
- `vault/projeto/decisoes.md` — log cronológico de decisões técnicas
- `vault/projeto/convencoes.md` — coding standards, naming, estrutura

### 1.5. Plugins recomendados (instalação manual)

Documentar no `vault/CLAUDE.md` quais plugins instalar via Community Plugins:
- BRAT (para 3D Graph)
- 3D Graph v2.4.1
- Folders to Graph
- Calendar

---

## Fase 2 — Comandos `/retomar` e `/salvar`

Claude Code suporta slash commands customizados via `.claude/commands/*.md`. Cada arquivo vira um comando.

### 2.1. `.claude/commands/retomar.md`

Instrui o Claude a:
1. Ler os 3 últimos arquivos em `vault/logs/` (`Get-ChildItem ... | Sort-Object LastWriteTime -Descending | Select -First 3`)
2. Ler `vault/projeto/decisoes.md`
3. Ler `graphify-out/GRAPH_REPORT.md` se existir
4. Imprimir resumo do estado e próximos passos

### 2.2. `.claude/commands/salvar.md`

Instrui o Claude a:
1. Criar `vault/logs/YYYY-MM-DD-{slug}.md` com frontmatter
2. Listar: o que foi feito, decisões, pendências, files modificados
3. Adicionar wikilinks para notas criadas/alteradas
4. Sugerir `git add . && git commit` (não executar — usuário decide)

---

## Fase 3 — Graphify (Knowledge Graph)

### 3.1. Instalação

```powershell
pip install graphifyy
graphify install   # instala skill em ~/.claude/skills/graphify/
```

### 3.2. Primeira execução

**Bloqueado até existir código-fonte.** Adicionar nota em `vault/projeto/decisoes.md` lembrando de rodar:

```powershell
cd "C:\Users\jacks\OneDrive\2º Cérebro\Scanner de imagens"
graphify . --obsidian --obsidian-dir ".\vault\graphify"
```

### 3.3. Git hook (após `git init`)

```powershell
graphify hook install
```

### 3.4. `.gitignore` (criar quando inicializar git)

```gitignore
# Graphify
graphify-out/cache/

# Staging de chats
claude-exports/

# Obsidian workspace state (mas versiona settings)
vault/.obsidian/workspace*.json
vault/.obsidian/cache
```

### 3.5. Atualizar `CLAUDE.md` da raiz

**MERGE crítico**: o `CLAUDE.md` raiz atualmente só tem regras `context-mode`. Vou **anexar** (sem remover o existente) seções:

- **Context Navigation (3 camadas)**: graph.json → vault → arquivos brutos
- **Stack do projeto**: Python + Docling (a confirmar) + DOCX export
- **Convenções Zettelkasten**: link para `vault/CLAUDE.md`
- **Comandos**: `/retomar`, `/salvar`

---

## Fase 4 — Pipeline de Importação de Chats

### 4.1. Pré-requisito

```powershell
pip install claude-conversation-extractor
```

### 4.2. `scripts/claude_to_obsidian.py`

Script Python que:
- Lê arquivos `.md` em `claude-exports/code/` e `claude-exports/web/`
- Detecta origem (Code vs Web)
- Aplica `KEYWORD_TAG_MAP` (python, ocr, docling, docx, markdown, scanner, etc.)
- Adiciona frontmatter (`type: chat`, `source`, `imported`, tags)
- Faz scan em `vault/permanent/` para inserir `[[wikilinks]]` para títulos detectados
- Move processados para `vault/chats/code/` ou `vault/chats/web/`

### 4.3. `scripts/sync_claude_obsidian.ps1` (PowerShell, não bash)

```powershell
# Substitui o sync_claude_obsidian.sh do guia (que é bash/Linux)
$proj    = "C:\Users\jacks\OneDrive\2º Cérebro\Scanner de imagens"
$exports = "$proj\claude-exports"
$vault   = "$proj\vault"
$log     = "$proj\scripts\sync.log"

"[$(Get-Date)] Sync iniciado" | Out-File $log -Append
claude-extract --all --output "$exports\code" 2>&1 | Out-File $log -Append
python "$proj\scripts\claude_to_obsidian.py" --export-dir $exports --vault-dir $vault --move 2>&1 | Out-File $log -Append
"[$(Get-Date)] Sync concluido" | Out-File $log -Append
```

### 4.4. Agendamento via Task Scheduler (não cron)

Adaptação Windows-native do `crontab` Linux. Documentar (não executar):

```powershell
$action  = New-ScheduledTaskAction -Execute "powershell.exe" -Argument '-File "C:\...\scripts\sync_claude_obsidian.ps1"'
$trigger = New-ScheduledTaskTrigger -Daily -At 22:00
Register-ScheduledTask -TaskName "ClaudeChatSync" -Action $action -Trigger $trigger
```

### 4.5. Bulk export do Claude Web

Documentar manualmente: extensão "Export Claude Chat to Markdown" → salvar em `claude-exports/web/`.

---

## Arquivos críticos a criar/modificar

| Path | Ação | Conteúdo |
|------|------|----------|
| `vault/CLAUDE.md` | CREATE | Regras Zettelkasten + comandos |
| `vault/templates/nota-padrao.md` | CREATE | Template com frontmatter |
| `vault/projeto/arquitetura.md` | CREATE | MOC do projeto |
| `vault/projeto/decisoes.md` | CREATE | Log de decisões |
| `vault/projeto/convencoes.md` | CREATE | Coding standards |
| `.claude/commands/retomar.md` | CREATE | Comando `/retomar` |
| `.claude/commands/salvar.md` | CREATE | Comando `/salvar` |
| `scripts/claude_to_obsidian.py` | CREATE | Processador de chats |
| `scripts/sync_claude_obsidian.ps1` | CREATE | Automação Windows |
| `CLAUDE.md` (raiz) | EDIT (append) | + Context Navigation + stack + convenções |
| `.gitignore` | CREATE | Excluir cache/exports |

---

## Verificação end-to-end

1. **Vault**: abrir Obsidian → "Open folder as vault" → selecionar `vault\` → confirmar que estrutura de pastas aparece e graph view funciona.
2. **CLAUDE.md merge**: rodar Claude Code na raiz e perguntar "qual a stack?" → resposta deve refletir o conteúdo novo do CLAUDE.md.
3. **Comandos**: digitar `/retomar` numa nova sessão → Claude lista `vault/logs/` (vazio inicialmente) e lê `decisoes.md`.
4. **Pipeline de chats**: rodar `scripts/sync_claude_obsidian.ps1` manualmente → verificar `vault/chats/code/` populado com frontmatter correto.
5. **Graphify** (post-código): após criar 2-3 arquivos `.py`, rodar `graphify . --obsidian` → confirmar `graphify-out/graph.json` e notas em `vault/graphify/`.
6. **Git hook**: `git init && graphify hook install` → fazer commit → grafo deve reconstruir automaticamente.

---

## Itens fora do escopo deste plano

- **Codificação do app de scanner em si** (Docling/OpenDataloader, FastAPI, DOCX export) — fica para um plano separado depois desta infraestrutura estar OK.
- **Decisão final Docling vs OpenDataloader vs híbrido** — confirmação adicional necessária com você antes de codar.
- **Conversão da pasta "Segundo Cérebro" do Notion em vault** — você optou por vault local; o conteúdo do Notion fica intocado.

---

## Próxima etapa após aprovação

Sair do plan mode e executar Fases 1 → 2 → 4 (Graphify só depois de existir código). Cada fase commitada separadamente para histórico limpo.
