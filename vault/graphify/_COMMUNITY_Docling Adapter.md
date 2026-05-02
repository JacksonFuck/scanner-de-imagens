---
type: community
cohesion: 0.67
members: 3
---

# Docling Adapter

**Cohesion:** 0.67 - moderately connected
**Members:** 3 nodes

## Members
- [[Adapter para Docling DocumentConverter.  Encapsula toda a interação com a API al]] - rationale - engine\docling_engine.py
- [[_validate_source()]] - code - engine\docling_engine.py
- [[docling_engine.py]] - code - engine\docling_engine.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Docling_Adapter
SORT file.name ASC
```

## Connections to other communities
- 3 edges to [[_COMMUNITY_Extraction Output]]
- 2 edges to [[_COMMUNITY_Input Validation]]
- 1 edge to [[_COMMUNITY_DOCX Export]]
- 1 edge to [[_COMMUNITY_Engine + Scan Models]]

## Top bridge nodes
- [[Adapter para Docling DocumentConverter.  Encapsula toda a interação com a API al]] - degree 4, connects to 3 communities
- [[docling_engine.py]] - degree 4, connects to 2 communities
- [[_validate_source()]] - degree 3, connects to 2 communities