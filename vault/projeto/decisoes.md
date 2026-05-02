---
title: Log de Decisões Técnicas
tags: [scanner, decisao, moc]
created: 2026-05-02
updated: 2026-05-02
status: active
type: moc
---

# Log de Decisões Técnicas

> ADR-style log. Cada decisão = uma seção com Status, Contexto, Decisão, Consequências.

## 2026-05-02 — Setup de infraestrutura de memória {#setup-infra}

**Status**: Aceito

**Contexto**: Projeto greenfield. Antes de codar, montar Obsidian + Graphify + pipeline de chats para evitar amnésia entre sessões e releitura de codebase.

**Decisão**:
- Vault local dentro do repo (`vault/`), não centralizado
- Obsidian já estava configurado na raiz do projeto (`.obsidian/` existe)
- Slash commands `/retomar` e `/salvar` em `.claude/commands/`
- Pipeline de chats via PowerShell (Windows-native), não bash

**Consequências**:
- Vault viaja com o repo no `git clone`
- Sem linking cross-projeto (trade-off aceito para greenfield)
- Task Scheduler do Windows substitui o cron do guia original

---

## 2026-05-02 — Motor de extração: Docling vs OpenDataloader {#motor-extracao}

**Status**: ✅ **ACEITO** — Docling primário, com fonte clonada localmente em `docling-main/docling-main/`

**Contexto**: Input do app são fotos JPG/PNG de páginas. A regra global do user (`~/.claude/rules/pdf-extraction-default.md`) define **opendataloader-pdf** como default — mas só aceita PDF.

**Opções avaliadas**:

| Opção | Aceita JPG | Layout/OCR | Export Markdown | Custo |
|-------|-----------|------------|-----------------|-------|
| **Docling** ✅ | Sim (`backend/image_backend.py`) | Sim (nativo) | Sim | Python deps grandes |
| OpenDataloader-PDF | **Não** | Sim | Sim | Já instalado global |
| Pillow → PDF → OpenDataloader | Indireto | Sim | Sim | Pipeline 2 etapas |

**Decisão**: **Docling primário**. Já temos a fonte clonada em `docling-main/docling-main/` (não usar `pip install docling` por enquanto — usar editable install se quisermos modificar internals).

**Consequências aceitas**:
- Documentar exceção à regra global no `CLAUDE.md` raiz ✅ (feito)
- Backend a usar: `docling.backend.image_backend.DoclingParseDocumentBackend` (a confirmar API exata na implementação)
- Adicionar `docling-main/` ao `.gitignore` para não versionar a fonte clonada (~MB de código de terceiros)
- OpenDataloader-PDF fica como **fallback** quando o input já for PDF
- Avaliar se vamos usar `pip install docling` (release) ou `pip install -e ./docling-main/docling-main` (dev install com a versão clonada)

**TODO de implementação**:
- [ ] Decidir entre release vs editable install do Docling
- [ ] Validar que `image_backend.py` aceita JPG/PNG diretamente (vs. precisar converter para PDF primeiro)
- [ ] Configurar OCR engine do Docling (EasyOCR vs Tesseract vs RapidOCR)
- [ ] Avaliar uso do `picture_classifier` para detectar imagens dentro das páginas e preservá-las

---

## 2026-05-02 — Stack do MVP {#stack-mvp}

**Status**: ✅ ACEITO — implementado nesta sessão

| Decisão | Escolha | Por quê |
|---------|---------|---------|
| Install Docling | `pip install docling` (release, não editable) | Mais simples; `docling-main/` fica como referência |
| OCR engine | EasyOCR (default Docling) | Funciona bem em PT, sem instalação extra (Tesseract requer binário) |
| Image mode | `ImageRefMode.REFERENCED` | Imagens viram arquivos `.png` sibling do `.md`, não base64 inline |
| DOCX export | `pypandoc` + pandoc CLI | Preserva imagens e estrutura via passagem MD→DOCX (auto-download se faltar) |
| Storage | filesystem + manifest implícito | MinIO é overkill no MVP — pasta `<base>-images/` por arquivo |
| CLI framework | Typer + Rich | Type-safe, generation automática de `--help`, output bonito |
| API web | adiada — só CLI no MVP | YAGNI — primeiro validar a qualidade da extração |
| Build backend | hatchling | Padrão moderno, sem `setup.py` |
| Linter/formatter | ruff (lint + format unificado) | Mais rápido que black+isort+flake8 separados |

## 2026-05-02 — Múltiplos Pythons no PATH {#multiplos-pythons}

**Status**: ⚠️ Workaround aplicado — não há solução única

**Contexto**: Sistema tem 3 instalações de Python:
- `C:\Python313\` — bash usa este por padrão (com sys.path quebrado)
- `C:\Users\jacks\AppData\Local\Programs\Python\Python313\`
- `C:\Users\jacks\scoop\apps\python\current\` — onde `pip` está

**Decisão**: Usar caminho explícito `C:\Users\jacks\scoop\apps\python\current\python.exe` em scripts. Para uso interativo, **criar venv dedicado** ao projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

Isso isola o ambiente e evita o conflito.

## 2026-05-02 — Resultado de testes {#resultados-testes}

- 29 testes unitários passando (CLI, pipeline, validação engine)
- 1 teste skipped (smoke test com Docling — só roda se docling instalado)
- ruff: All checks passed
- CLI funcional: `python -m scanner --version`, `... convert --help`

## TODO — Próximas decisões

- [ ] Instalar Docling completo (`pip install docling`) — ~3-5 GB com torch+transformers+EasyOCR
- [ ] Testar com foto real e medir qualidade do OCR em português
- [ ] Avaliar pré-processamento (deskew/dewarp via Pillow ou OpenCV) antes do Docling
- [ ] Decidir se precisa pré-processamento adicional para fotos com curvatura de página
- [ ] Quando rodar Graphify: agora já temos `src/scanner/*.py` — pode rodar
- [ ] (futuro) API web FastAPI quando o pipeline core estiver estável
- [ ] (futuro) Suporte a batch async para processar diretórios grandes
