---
type: community
cohesion: 0.67
members: 4
---

# Input Validation

**Cohesion:** 0.67 - moderately connected
**Members:** 4 nodes

## Members
- [[Expande um caminho arquivo único → arquivo; pasta → todos os suportados.]] - rationale - pipeline.py
- [[Input inexistente, formato não suportado ou corrompido.]] - rationale - errors.py
- [[InvalidInputError]] - code - errors.py
- [[collect_inputs()]] - code - pipeline.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Input_Validation
SORT file.name ASC
```

## Connections to other communities
- 7 edges to [[_COMMUNITY_Engine + Scan Models]]
- 5 edges to [[_COMMUNITY_CLI Layer]]
- 4 edges to [[_COMMUNITY_Pipeline Orchestrator]]
- 4 edges to [[_COMMUNITY_Extraction Output]]
- 2 edges to [[_COMMUNITY_Scan Result Model]]
- 2 edges to [[_COMMUNITY_Docling Adapter]]
- 1 edge to [[_COMMUNITY_Error Hierarchy]]

## Top bridge nodes
- [[InvalidInputError]] - degree 25, connects to 7 communities
- [[collect_inputs()]] - degree 4, connects to 2 communities
- [[Expande um caminho arquivo único → arquivo; pasta → todos os suportados.]] - degree 3, connects to 1 community