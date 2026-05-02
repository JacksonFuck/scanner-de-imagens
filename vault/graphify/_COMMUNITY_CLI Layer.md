---
type: community
cohesion: 0.18
members: 17
---

# CLI Layer

**Cohesion:** 0.18 - loosely connected
**Members:** 17 nodes

## Members
- [[CLI Typer + Rich.  Apresentação fina sobre `pipeline.scan_batch`. Toda lógica de]] - rationale - cli.py
- [[Configura logging com base nas flags globais.]] - rationale - cli.py
- [[Converte foto(s) de página(s) em Markdown estruturado.      Exemplos        sca]] - rationale - cli.py
- [[Erro base do scanner — qualquer falha esperada herda daqui.]] - rationale - errors.py
- [[Exception]] - code
- [[Formatos de saída solicitáveis.]] - rationale - pipeline.py
- [[Imprime tabela Rich com sucessos e falhas.]] - rationale - cli.py
- [[OutputFormat]] - code - pipeline.py
- [[Scanner de Imagens — OCR de fotos de páginas para Markdown estruturado + DOCX.]] - rationale - __init__.py
- [[ScannerError]] - code - errors.py
- [[StrEnum]] - code
- [[__init__.py]] - code - __init__.py
- [[_render_results()]] - code - cli.py
- [[_version_callback()]] - code - cli.py
- [[cli.py]] - code - cli.py
- [[convert()]] - code - cli.py
- [[main()]] - code - cli.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/CLI_Layer
SORT file.name ASC
```

## Connections to other communities
- 5 edges to [[_COMMUNITY_Input Validation]]
- 4 edges to [[_COMMUNITY_Engine + Scan Models]]
- 2 edges to [[_COMMUNITY_Extraction Output]]
- 1 edge to [[_COMMUNITY_Error Hierarchy]]
- 1 edge to [[_COMMUNITY_DOCX Export]]
- 1 edge to [[_COMMUNITY_Pipeline Orchestrator]]
- 1 edge to [[_COMMUNITY_Scan Result Model]]

## Top bridge nodes
- [[ScannerError]] - degree 11, connects to 4 communities
- [[Scanner de Imagens — OCR de fotos de páginas para Markdown estruturado + DOCX.]] - degree 7, connects to 4 communities
- [[OutputFormat]] - degree 10, connects to 3 communities
- [[convert()]] - degree 5, connects to 2 communities
- [[Formatos de saída solicitáveis.]] - degree 3, connects to 2 communities