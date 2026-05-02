# Scanner de Imagens — Handoff

> Documento de transferência de contexto. Cobre tudo que foi construído, decisões tomadas, como rodar, como evoluir, e onde achar o quê.

**Data**: 2026-05-02
**Versão atual**: 0.1.0
**Status**: MVP funcional, testado em produção (69 fotos reais convertidas)

---

## Sumário

1. [Visão geral](#1-visão-geral)
2. [Arquitetura](#2-arquitetura)
3. [Stack tecnológica](#3-stack-tecnológica)
4. [Instalação do zero](#4-instalação-do-zero)
5. [Uso da CLI](#5-uso-da-cli)
6. [Uso programático (API Python)](#6-uso-programático-api-python)
7. [Pós-processamento de MDs](#7-pós-processamento-de-mds)
8. [Estrutura do repositório](#8-estrutura-do-repositório)
9. [Decisões arquiteturais](#9-decisões-arquiteturais)
10. [Performance medida](#10-performance-medida)
11. [Troubleshooting](#11-troubleshooting)
12. [Memória persistente do projeto](#12-memória-persistente-do-projeto)
13. [Knowledge graph (Graphify)](#13-knowledge-graph-graphify)
14. [Roadmap e pendências](#14-roadmap-e-pendências)
15. [Histórico de commits](#15-histórico-de-commits)

---

## 1. Visão geral

**Scanner de Imagens** é um aplicativo Python que recebe **fotografias de páginas de livros, artigos ou documentos** e gera saída estruturada em **Markdown** + **DOCX**, preservando texto, tabelas, layout e imagens embutidas.

### Caso de uso real validado
- 69 fotos da pasta `GESTÃO DE PS` (jornal/apostila médica fotografada)
- Output: 69 MDs + 69 DOCXs + 1 livro consolidado (`gestao-pronto-socorro.{md,docx}`)
- Tempo total: ~9 minutos com GPU (RTX 3060)

### Diferenciais
- **OCR de qualidade**: EasyOCR com português + inglês, escala 3x
- **Detecção de tabelas**: TableFormer preserva colspan/rowspan
- **GPU acceleration**: 7x mais rápido que CPU (5s vs 35s por foto)
- **Modos de saída**: arquivos separados ou livro consolidado (`--merge`)
- **Pós-processador**: dicionário curado corrige acentos perdidos por OCRs antigos sem PT
- **Fallback inteligente**: pandoc auto-baixado se faltar; Tesseract como engine alternativo

---

## 2. Arquitetura

### Camadas do app

```
┌────────────────────────────────────────────┐
│  CLI (Typer + Rich)         scanner.cli    │  apresentação
├────────────────────────────────────────────┤
│  Pipeline (orquestrador)    scanner.pipeline │  fluxo
├────────────────────────────────────────────┤
│  Engine (adapter Docling)   scanner.engine │  OCR + layout
│  Export (md, docx)          scanner.export │  formato de saída
├────────────────────────────────────────────┤
│  Errors (exceções)          scanner.errors │  tratamento
└────────────────────────────────────────────┘
```

### Fluxo de uma conversão

```
foto.jpg → DoclingEngine.extract()
            ├── DocumentConverter (Docling)
            │     ├── EasyOCR (lang=pt,en, GPU)
            │     ├── Layout DETR (heron model)
            │     └── TableFormer
            └── DoclingDocument.save_as_markdown()
                  ├── escreve foto.md em output/
                  └── extrai imagens em foto-images/
                        ↓
                  (opcional) MD → DOCX via pypandoc
```

### Componentes principais

| Módulo | Responsabilidade |
|--------|------------------|
| `cli.py` | Typer CLI, flags `--device`, `--ocr-lang`, `--ocr-engine`, `--merge`, `--format` |
| `pipeline.py` | `scan()`, `scan_batch()`, `merge_results()`, `collect_inputs()` |
| `engine/docling_engine.py` | Adapter sobre `DocumentConverter`, configura OCR + GPU + scale |
| `export/markdown.py` | (helper genérico — Docling escreve direto) |
| `export/docx.py` | MD → DOCX via pypandoc, com auto-detecção de pandoc cacheado |
| `errors.py` | Hierarquia `ScannerError` → `Invalid/Conversion/Configuration` |

---

## 3. Stack tecnológica

### Runtime
- **Python**: 3.11+ (testado com 3.14 do scoop; 3.13 também funciona)
- **PyTorch**: 2.11.0+cu128 (GPU CUDA 12.8) ou 2.11.0+cpu
- **Docling**: 2.92.0 (com `docling-slim`)
- **EasyOCR**: 1.7.2 (instalado separado — não vem com `docling-slim`)

### CLI
- **Typer**: 0.25.x (geração automática de help, type-safe)
- **Rich**: 15.x (output bonito, tabelas, progressbar)

### Conversão
- **pypandoc**: 1.x (auto-baixa pandoc 3.9.0.2)
- **pandoc**: 3.9.0.2 (auto-instalado em `~/AppData/Local/Pandoc/`)

### Dev tooling
- **ruff**: lint + format (substitui black/isort/flake8)
- **pytest**: 9.x com `pytest-cov`
- **mypy**: strict mode em `src/scanner`
- **hatchling**: build backend (substitui setuptools)

### Hardware testado
- **GPU**: NVIDIA RTX 3060, 12 GB VRAM, driver 595.79 → CUDA 12.8 wheels
- **CPU**: também funciona (mais lento, ~7x)

---

## 4. Instalação do zero

### Pré-requisitos
- Python 3.11+ (3.13 ou 3.14 recomendado)
- Git (opcional mas recomendado)
- GPU NVIDIA com CUDA (opcional, dá 7x speedup)

### Passos

```powershell
# 1. clonar
git clone <url-do-repo>
cd "Scanner de imagens"

# 2. criar venv (recomendado para isolar)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. instalar deps mínimas + projeto
pip install -e ".[dev]"

# 4. instalar EasyOCR (não vem com docling-slim)
pip install easyocr

# 5. (opcional) instalar PyTorch com CUDA 12.8 para GPU
pip install --force-reinstall torch torchvision --index-url https://download.pytorch.org/whl/cu128

# 6. validar
python -m scanner --version           # deve imprimir "scanner 0.1.0"
python -m pytest -q -m "not slow"    # 29 passing
```

### Pandoc
Não precisa instalar. O `pypandoc.download_pandoc()` baixa automaticamente para `~/AppData/Local/Pandoc/` na primeira conversão DOCX.

### Tesseract (opcional, alternativa ao EasyOCR)
```powershell
# Download português traineddata
mkdir tessdata-portuguese
# baixar manualmente:
#   https://github.com/tesseract-ocr/tessdata_best/raw/main/por.traineddata
#   https://github.com/tesseract-ocr/tessdata_best/raw/main/eng.traineddata

# Tesseract executável: instalar UB Mannheim build
#   https://github.com/UB-Mannheim/tesseract/wiki

# usar no scanner:
python -m scanner convert ./foto.jpg --ocr-engine tesseract --tessdata ./tessdata-portuguese
```

---

## 5. Uso da CLI

### Comando básico
```powershell
python -m scanner convert <input> [opções]
```

### Argumentos
- `<input>`: arquivo único (.jpg/.png/.pdf) **ou** pasta com vários

### Opções principais

| Flag | Default | Descrição |
|------|---------|-----------|
| `-o, --output PATH` | `./output` | Pasta de saída |
| `-f, --format` | `md` | `md` \| `docx` \| `both` |
| `--device` | `auto` | `auto` (detecta GPU) \| `cuda` \| `cpu` |
| `--ocr-lang` | `pt,en` | Idiomas separados por vírgula |
| `--ocr-engine` | `easyocr` | `easyocr` \| `tesseract` |
| `--tessdata PATH` | (auto) | Diretório com `*.traineddata` (Tesseract) |
| `--merge / --no-merge` | (pergunta) | Consolidar múltiplas imagens em arquivo único |
| `--merge-name` | `combined` | Nome base do arquivo consolidado |
| `--no-ocr` | `False` | Desabilita OCR (útil para PDFs com texto seletivo) |
| `--no-tables` | `False` | Desabilita reconhecimento de tabelas |
| `-v, --verbose` | `False` | Logs DEBUG |

### Exemplos práticos

```powershell
# foto única → markdown
python -m scanner convert foto.jpg -o ./output

# pasta inteira → MD + DOCX, GPU, livro consolidado
python -m scanner convert ./fotos -o ./output -f both --device cuda --merge --merge-name "meu-livro"

# usar Tesseract com tessdata local
python -m scanner convert ./fotos --ocr-engine tesseract --tessdata ./tessdata-portuguese

# forçar idiomas específicos
python -m scanner convert ./doc.pdf --ocr-lang "pt,en,es"

# debug verbose
python -m scanner -v convert ./foto.jpg
```

### Modo interativo (merge)
Quando há múltiplas imagens E `--merge`/`--no-merge` não passou, o CLI **pergunta**:
```
Consolidar as 69 imagens em UM único arquivo? [y/N]:
```
Em pipes/CI (não-TTY), default é `False`.

---

## 6. Uso programático (API Python)

```python
from pathlib import Path
from scanner import scan, scan_batch, ScanRequest, OutputFormat

# 1. Conversão única
result = scan(ScanRequest(
    source=Path("foto.jpg"),
    output_dir=Path("./output"),
    formats=OutputFormat.BOTH,
    device="cuda",
    ocr_languages=("pt", "en"),
))
print(result.markdown_path)   # output/foto.md
print(result.docx_path)       # output/foto.docx
print(result.images)          # tuple de Paths
print(result.page_count)      # 1

# 2. Batch reusando engine (instância cara — ~3s pra carregar)
from scanner.pipeline import scan_batch, collect_inputs

inputs = collect_inputs(Path("./fotos"))   # filtra por extensão suportada
batch = scan_batch(
    inputs,
    Path("./output"),
    formats=OutputFormat.BOTH,
    device="cuda",
    merge=True,
    merge_name="livro",
)
print(f"OK: {len(batch.successes)} | Falhas: {len(batch.failures)}")
for src, exc in batch.failures:
    print(f"  - {src.name}: {exc}")
```

### Exceções
Todas herdam de `scanner.errors.ScannerError`:
- `InvalidInputError`: arquivo não existe ou extensão não suportada
- `ConversionError`: Docling falhou
- `ConfigurationError`: dependência faltando, engine inválido

---

## 7. Pós-processamento de MDs

### Quando usar
Quando você já tem MDs gerados pelo scanner mas com OCR antigo (sem PT) e quer corrigir acentos sem re-rodar.

### Comando

```powershell
python scripts/postprocess_md.py \
    --input-dir output/gestao-ps \
    --output-dir output/gestao-ps-corrigido \
    --merge \
    --merge-name "livro-consolidado" \
    --title "Meu Livro" \
    --copy-images
```

### O que faz
1. **Dicionário** de ~150 palavras PT-BR comuns sem acento → forma correta (ção, ções, áéíóú em palavras frequentes)
2. **Regex**: corrige espaços antes de pontuação, ` ; ` → `, ` em meio de palavra
3. **Heurística "0" → "O"** no início de palavras em contexto português
4. **Preserva** blocos de código markdown (``` e `inline`)
5. **`--merge`**: gera arquivo único com sumário (ToC)

### Limitações
- Cobre ~80% dos casos comuns. Palavras raras/jargões ficam como estão.
- Não corrige semântica/fluxo — só correções deterministicas.

---

## 8. Estrutura do repositório

```
.
├── CLAUDE.md                    # Regras context-mode + Context Navigation + stack
├── README.md                    # README curto (apontar para HANDOFF)
├── docs/
│   └── HANDOFF.md              # ESTE DOCUMENTO
├── pyproject.toml              # hatchling, deps, ruff, mypy, pytest
├── .python-version             # 3.13
├── .gitignore                  # cache, logs, output, etc.
├── src/scanner/                # package principal
│   ├── __init__.py             # version + API pública
│   ├── __main__.py             # python -m scanner
│   ├── cli.py                  # Typer CLI
│   ├── pipeline.py             # scan, scan_batch, merge_results
│   ├── errors.py               # exceções
│   ├── engine/
│   │   ├── __init__.py
│   │   └── docling_engine.py   # adapter Docling
│   └── export/
│       ├── __init__.py
│       ├── markdown.py
│       └── docx.py             # pypandoc + auto-detect cached pandoc
├── tests/                      # 29 testes unitários + 1 slow
│   ├── conftest.py
│   ├── test_cli.py
│   ├── test_engine.py
│   └── test_pipeline.py
├── scripts/
│   ├── postprocess_md.py       # corretor de acentos + merge
│   ├── claude_to_obsidian.py   # pipeline import de chats Claude → Obsidian
│   └── sync_claude_obsidian.ps1 # automação Windows do pipeline acima
├── samples/                    # imagens de teste (gitignored)
│   └── README.md
├── tessdata-portuguese/        # Tesseract por.traineddata + eng + osd (~22MB)
├── output/                     # gitignored — outputs de runs
├── claude-exports/             # gitignored — staging de chats
├── graphify-out/               # knowledge graph (versionado parcialmente)
│   ├── graph.json
│   ├── graph.html
│   ├── GRAPH_REPORT.md
│   └── manifest.json
├── vault/                      # Obsidian vault local (memória persistente)
│   ├── CLAUDE.md
│   ├── projeto/                # MOCs
│   │   ├── arquitetura.md
│   │   ├── decisoes.md
│   │   └── convencoes.md
│   ├── logs/                   # session logs (/salvar)
│   ├── chats/                  # imports automáticos
│   └── graphify/               # 81 notas geradas pelo Graphify
├── .claude/
│   └── commands/
│       ├── retomar.md          # /retomar
│       └── salvar.md           # /salvar
├── .obsidian/                  # config Obsidian (workspace.json gitignored)
└── docling-main/               # gitignored — clone fonte do Docling como referência
```

---

## 9. Decisões arquiteturais

Documentadas com detalhe em `vault/projeto/decisoes.md`. Resumo:

| Tema | Decisão | Por quê |
|------|---------|---------|
| Motor extração | Docling (não OpenDataloader-PDF) | Aceita JPG/PNG nativos; OpenDataloader é PDF-only |
| OCR engine | EasyOCR primário, Tesseract opcional | EasyOCR melhor PT acentos, Tesseract melhor texto impresso clean |
| Idiomas OCR | `pt,en` explícito | Default Docling é `fr,de,es,en` — sem PT! |
| Image scale | 3.0x (default 2.0) | Mais detalhe para OCR de fotos |
| DOCX | pypandoc + pandoc CLI | Preserva imagens via passagem MD→DOCX |
| Storage | filesystem | MinIO é overkill no MVP |
| CLI framework | Typer + Rich | Type-safe, output bonito |
| API web | adiada | YAGNI até ter pipeline core estável |
| Build backend | hatchling | Padrão moderno |
| Linter | ruff (lint+format) | Mais rápido que black+isort+flake8 |
| GPU | PyTorch 2.11+cu128 | Wheels para Python 3.14; cu124/126/127 não tem |
| Vault Obsidian | local no projeto | Vault viaja com o repo |
| Knowledge graph | Graphify modo AST (0 tokens) | Persistente entre sessões |

---

## 10. Performance medida

### Batch real: 69 fotos da pasta GESTÃO DE PS

| Configuração | Tempo/foto | Tempo total |
|---|---|---|
| **CPU** (PyTorch+cpu) | ~35s | ~40 min estimado |
| **GPU** (RTX 3060 + cu128) | ~5s | **~9 min real** ⚡ |

**Speedup**: 7x com GPU.

### Tamanhos típicos de output (1 página fotografada)
- `.md`: 2-5 KB
- `.docx`: 12-50 KB
- imagens extraídas: 20-200 KB cada (PNG, scale 3x)

### Custo de tokens
- Pipeline padrão: **0 tokens LLM** (tudo OCR + algoritmos)
- Graphify modo AST: **0 tokens**
- Pós-processador: **0 tokens** (regex + dicionário)

---

## 11. Troubleshooting

### "ModuleNotFoundError: easyocr"
`docling-slim` não inclui EasyOCR. Instale:
```powershell
pip install easyocr
```

### "Could not find a version that satisfies the requirement torch (cu124)"
PyTorch CUDA não tem wheels para sua versão Python. Tente:
```powershell
pip install --force-reinstall torch torchvision --index-url https://download.pytorch.org/whl/cu128
```
(Para Python 3.14, **somente cu128** funciona.)

### CUDA disponível mas não é usado
1. Confirmar: `python -c "import torch; print(torch.cuda.is_available())"`
2. Forçar via flag: `python -m scanner convert ... --device cuda`
3. Se ainda CPU, ver log: deve aparecer `Accelerator device: 'cuda:0'`

### Pandoc rate limit (HTTP 403)
Aconteceu na primeira sessão de testes. Causa: cada chamada DOCX disparava `download_pandoc()` porque o `_ensure_pandoc()` antigo não procurava no cache.

**Fix aplicado** (commit `9fd4d0c`): agora procura em `~/AppData/Local/Pandoc/` antes de baixar.

### "Acentos virando ASCII (ção → cao)"
OCR rodou com idiomas errados. Verifique:
```powershell
python -m scanner convert ... --ocr-lang "pt,en"
```
Para corrigir MDs já gerados, use o pós-processador.

### Encoding UnicodeError no Windows
PowerShell 5.1 usa cp1252 que quebra com `→`/`✅`. Sempre passe `encoding='utf-8'` em `Path.write_text()`.

### Múltiplos Pythons no PATH
Sistema pode ter Python do Microsoft Store, scoop, e instalado oficial. Use caminho explícito ou venv dedicado:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Graphify "Run 'graphify --help' for usage"
`graphify .` no terminal não funciona — só funciona via skill no Claude Code (`/graphify`). Para CLI direto, use:
```powershell
graphify update ./src   # incremental
```

---

## 12. Memória persistente do projeto

### Vault Obsidian
Localizado em `vault/`. Estrutura Zettelkasten:

| Pasta | Conteúdo |
|-------|----------|
| `vault/projeto/` | MOCs: `arquitetura.md`, `decisoes.md`, `convencoes.md` |
| `vault/logs/` | Session logs (gerados por `/salvar`) |
| `vault/permanent/` | Notas atômicas consolidadas |
| `vault/inbox/` | Captura bruta |
| `vault/chats/` | Conversas Claude importadas (cron diário) |
| `vault/graphify/` | 81 notas auto-geradas pelo Graphify |

Abrir no Obsidian: "Open folder as vault" → selecionar a raiz do projeto.

### Slash commands custom
- `/retomar` (`.claude/commands/retomar.md`): lê últimos logs e decisões, resume estado
- `/salvar` (`.claude/commands/salvar.md`): cria session log no vault

### Pipeline de import de chats
- Script: `scripts/claude_to_obsidian.py` (Python idempotente)
- Automação: `scripts/sync_claude_obsidian.ps1` (PowerShell, agendável via Task Scheduler)

---

## 13. Knowledge graph (Graphify)

### Atual snapshot (commit `77545e4`)
- **68 nós**, 147 edges, 13 communities labeled
- **God nodes**: `InvalidInputError` (25), `DoclingEngine` (22), `ConversionError` (15)
- **81 notas Obsidian** geradas em `vault/graphify/`
- **HTML interativo**: `graphify-out/graph.html`
- **Custo**: 0 tokens (modo AST)

### Atualizar incrementalmente
```powershell
graphify update ./src
```

### Consultar
```powershell
graphify query "como o pipeline lida com formato DOCX"
graphify path "DoclingEngine" "Pipeline Orchestrator"
graphify explain "InvalidInputError"
```

### Re-rodar do zero (regenera tudo)
Via skill no Claude Code: `/graphify ./src --obsidian --obsidian-dir ./vault/graphify`

---

## 14. Roadmap e pendências

### Curto prazo (próxima sessão)
- [ ] Adicionar mais palavras ao dicionário do pós-processador (cobrir mais casos)
- [ ] Pré-processamento (deskew/dewarp) via Pillow para fotos com curvatura
- [ ] Exposição da flag `--scale` na CLI (atualmente fixada em 3.0 no engine)

### Médio prazo
- [ ] **Integração LLM (Claude API)** para casos ambíguos do pós-processador (revisão semântica)
- [ ] **API web FastAPI** quando o pipeline core estiver maduro
- [ ] Suporte a batch async para diretórios grandes (>1000 fotos)
- [ ] Web UI simples (drag-drop de fotos)

### Longo prazo
- [ ] Suporte a outros formatos: scanner físico (TWAIN/WIA), captura via webcam
- [ ] Dashboards de qualidade (% acentos corretos, % palavras desconhecidas)
- [ ] Pipeline com múltiplos engines em paralelo + voting (consensus OCR)

### Pendências técnicas
- [ ] CI/CD via GitHub Actions (lint + tests no push)
- [ ] Releases automatizadas com `gh release create`
- [ ] Dockerfile para distribuição
- [ ] Documentação de API com mkdocs ou sphinx

---

## 15. Histórico de commits

```
ffa47a5  feat: Tesseract OCR + post-processor for accent correction
5c2f015  feat: PT OCR + merge to single file + interactive prompt
9fd4d0c  feat(engine): add GPU/CUDA support + fix pandoc cache lookup
72771d2  chore(gitignore): fix unicode filename glob pattern
3310b71  chore: untrack pandoc.msi, test logs, and stray graphify cache
8af8311  fix(engine): use save_as_markdown API (Docling 2.92+)
77545e4  feat(graphify): generate initial knowledge graph for src/
6672626  chore: bootstrap MVP do Scanner de Imagens com infra de memória persistente
```

### Sessões trabalhadas

#### Sessão 1 (2026-05-02) — Bootstrap
- Infraestrutura completa: Vault Obsidian, slash commands, pipeline de chats
- MVP do app: Docling adapter, pipeline, CLI, exports
- Knowledge graph inicial via Graphify
- 30 testes passing, ruff clean
- Validação ponta-a-ponta com 2 imagens (paper + jornal)

#### Sessão 2 (2026-05-02) — Performance + GPU
- PyTorch CUDA cu128 instalado (descoberta: Python 3.14 só tem wheels cu128)
- Engine ganha flag `--device` (auto/cuda/cpu)
- Bug fix: API do Docling 2.92 mudou `export_to_markdown` → `save_as_markdown`
- Bug fix: pandoc cache não detectado (rate limit 403 GitHub)
- Batch real: 69 fotos GESTÃO DE PS, ~9 min com GPU

#### Sessão 3 (2026-05-02) — Qualidade do OCR
- Idiomas OCR explícitos `pt,en` (default Docling é `fr,de,es,en` — falta PT!)
- Image scale 2.0 → 3.0 para mais detalhe
- Tesseract como engine alternativo (TesseractCliOcrOptions)
- Por.traineddata baixado e configurado
- Pós-processador `scripts/postprocess_md.py` com dicionário PT-BR
- Livro consolidado: 69 páginas → `gestao-pronto-socorro.{md,docx}`

---

## Para a próxima sessão

Use `/retomar` ao iniciar. O comando lê:
1. Últimos 3 session logs em `vault/logs/`
2. `vault/projeto/decisoes.md`
3. `graphify-out/GRAPH_REPORT.md`

E imprime resumo do estado atual + próximos passos.

Ao finalizar, use `/salvar [slug]` para gerar log da sessão.

---

## Contato e licença

- **Autor**: Jackson (jacksontorax@gmail.com)
- **Licença**: MIT
- **Repositório**: https://github.com/JacksonFuck/scanner-de-imagens
