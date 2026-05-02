---
type: community
cohesion: 1.00
members: 2
---

# Error Hierarchy

**Cohesion:** 1.00 - tightly connected
**Members:** 2 nodes

## Members
- [[Exceções específicas do scanner.  Hierarquia simples tudo herda de `ScannerErro]] - rationale - errors.py
- [[errors.py]] - code - errors.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Error_Hierarchy
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_CLI Layer]]
- 1 edge to [[_COMMUNITY_Input Validation]]
- 1 edge to [[_COMMUNITY_Extraction Output]]
- 1 edge to [[_COMMUNITY_DOCX Export]]

## Top bridge nodes
- [[errors.py]] - degree 5, connects to 4 communities