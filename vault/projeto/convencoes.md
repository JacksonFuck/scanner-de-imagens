---
title: Convenções de Código e Estrutura
tags: [scanner, convencoes, moc]
created: 2026-05-02
updated: 2026-05-02
status: active
type: moc
---

# Convenções de Código e Estrutura

## Linguagem e ferramentas

- **Python 3.13** (já instalado no sistema)
- **Package manager**: `pip` (eventualmente migrar para `uv` quando o projeto crescer)
- **Linter/formatter**: `ruff` (lint + format unificado)
- **Type checker**: `mypy` em modo `strict` apenas para módulos do core
- **Testes**: `pytest` + `pytest-cov`

## Estrutura de pastas (provisória — atualizar quando codar)

```
src/
├── scanner/
│   ├── __init__.py
│   ├── ingest.py         # recebe fotos
│   ├── preprocess.py     # deskew, denoise
│   ├── ocr/
│   │   ├── docling_engine.py
│   │   └── opendataloader_engine.py
│   ├── render/
│   │   ├── markdown.py
│   │   └── docx.py
│   └── cli.py
tests/
└── (espelha src/)
```

## Naming

| Tipo | Padrão | Exemplo |
|------|--------|---------|
| Módulos | snake_case | `docling_engine.py` |
| Classes | PascalCase | `MarkdownRenderer` |
| Funções/vars | snake_case | `extract_text` |
| Constantes | UPPER_SNAKE | `DEFAULT_DPI` |
| Pastas no vault | kebab-case | `docling-pipeline.md` |

## Imports

- **Absolutos sempre**: `from scanner.ocr import docling_engine`
- **Não** usar relativos profundos (`from ..ocr import ...`)
- Ordem: stdlib → third-party → local (separadas por linha em branco)

## Error handling

- Validar entrada na **borda** do sistema (CLI, API)
- Lançar exceções específicas (`InvalidImageError`, `OCRFailedError`), nunca `Exception` genérica
- Log de erro com contexto (filename, page number) — usar `logging` stdlib
- Nunca engolir exceção silenciosamente

## Commits

Conventional commits:
- `feat:` nova funcionalidade
- `fix:` bug
- `refactor:` mudança sem alterar comportamento
- `docs:` documentação (inclui notas no vault)
- `chore:` tooling, deps, configs
- `test:` testes

Exemplos:
- `feat: add Docling engine adapter`
- `docs(vault): register decision on Docling vs OpenDataloader`

## Testes

- Cobertura mínima: **80%** para módulos do core
- Fixtures em `tests/fixtures/` — incluir 3-5 fotos de páginas reais (com permissão)
- Testes lentos marcados com `@pytest.mark.slow` e excluídos do CI rápido

## Links

- [[arquitetura]]
- [[decisoes]]
