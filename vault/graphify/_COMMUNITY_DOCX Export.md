---
type: community
cohesion: 0.36
members: 9
---

# DOCX Export

**Cohesion:** 0.36 - loosely connected
**Members:** 9 nodes

## Members
- [[.__init__()]] - code - engine\docling_engine.py
- [[ConfigurationError]] - code - errors.py
- [[Configuração inválida (engine não disponível, pandoc faltando, etc.).]] - rationale - errors.py
- [[Conversão Markdown → DOCX usando pandoc.  Decisão registrada em `vaultprojetod]] - rationale - export\docx.py
- [[Converte um arquivo Markdown para DOCX preservando imagens e estrutura.      Arg]] - rationale - export\docx.py
- [[Garante que pandoc está disponível. Tenta auto-download se necessário.]] - rationale - export\docx.py
- [[_ensure_pandoc()]] - code - export\docx.py
- [[docx.py]] - code - export\docx.py
- [[write_docx()]] - code - export\docx.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/DOCX_Export
SORT file.name ASC
```

## Connections to other communities
- 8 edges to [[_COMMUNITY_Extraction Output]]
- 2 edges to [[_COMMUNITY_Engine + Scan Models]]
- 1 edge to [[_COMMUNITY_Error Hierarchy]]
- 1 edge to [[_COMMUNITY_CLI Layer]]
- 1 edge to [[_COMMUNITY_Docling Adapter]]
- 1 edge to [[_COMMUNITY_Pipeline Orchestrator]]

## Top bridge nodes
- [[ConfigurationError]] - degree 15, connects to 5 communities
- [[write_docx()]] - degree 6, connects to 2 communities
- [[Conversão Markdown → DOCX usando pandoc.  Decisão registrada em `vaultprojetod]] - degree 3, connects to 1 community
- [[Converte um arquivo Markdown para DOCX preservando imagens e estrutura.      Arg]] - degree 3, connects to 1 community
- [[Garante que pandoc está disponível. Tenta auto-download se necessário.]] - degree 3, connects to 1 community