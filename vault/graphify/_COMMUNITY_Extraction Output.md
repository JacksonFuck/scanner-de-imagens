---
type: community
cohesion: 0.43
members: 7
---

# Extraction Output

**Cohesion:** 0.43 - moderately connected
**Members:** 7 nodes

## Members
- [[.extract()]] - code - engine\docling_engine.py
- [[ConversionError]] - code - errors.py
- [[ExtractionResult]] - code - engine\docling_engine.py
- [[Extrai conteúdo do arquivo `source` salvando imagens em `artifacts_dir`.]] - rationale - engine\docling_engine.py
- [[Falha durante extração via Docling ou conversão para DOCX.]] - rationale - errors.py
- [[Resultado da extração — payload puro, sem efeitos colaterais.]] - rationale - engine\docling_engine.py
- [[Wrapper fino do `DocumentConverter` do Docling.      Inicialização cara (carrega]] - rationale - engine\docling_engine.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Extraction_Output
SORT file.name ASC
```

## Connections to other communities
- 8 edges to [[_COMMUNITY_DOCX Export]]
- 4 edges to [[_COMMUNITY_Input Validation]]
- 3 edges to [[_COMMUNITY_Engine + Scan Models]]
- 3 edges to [[_COMMUNITY_Docling Adapter]]
- 2 edges to [[_COMMUNITY_CLI Layer]]
- 1 edge to [[_COMMUNITY_Error Hierarchy]]

## Top bridge nodes
- [[ConversionError]] - degree 15, connects to 5 communities
- [[ExtractionResult]] - degree 6, connects to 3 communities
- [[Wrapper fino do `DocumentConverter` do Docling.      Inicialização cara (carrega]] - degree 4, connects to 3 communities
- [[.extract()]] - degree 5, connects to 2 communities
- [[Resultado da extração — payload puro, sem efeitos colaterais.]] - degree 4, connects to 2 communities