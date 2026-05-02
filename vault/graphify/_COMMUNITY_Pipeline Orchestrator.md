---
type: community
cohesion: 0.40
members: 6
---

# Pipeline Orchestrator

**Cohesion:** 0.40 - moderately connected
**Members:** 6 nodes

## Members
- [[Orquestrador — costura ingest → engine → exports.  Função pública `scan()` é o p]] - rationale - pipeline.py
- [[Roda o pipeline para UM arquivo.      Reuse `engine` quando processar múltiplos]] - rationale - pipeline.py
- [[_validate_request()]] - code - pipeline.py
- [[pipeline.py]] - code - pipeline.py
- [[scan()]] - code - pipeline.py
- [[total()]] - code - pipeline.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Pipeline_Orchestrator
SORT file.name ASC
```

## Connections to other communities
- 7 edges to [[_COMMUNITY_Engine + Scan Models]]
- 4 edges to [[_COMMUNITY_Input Validation]]
- 2 edges to [[_COMMUNITY_Scan Result Model]]
- 1 edge to [[_COMMUNITY_CLI Layer]]
- 1 edge to [[_COMMUNITY_Markdown Export]]
- 1 edge to [[_COMMUNITY_DOCX Export]]

## Top bridge nodes
- [[pipeline.py]] - degree 10, connects to 4 communities
- [[scan()]] - degree 8, connects to 4 communities
- [[Orquestrador — costura ingest → engine → exports.  Função pública `scan()` é o p]] - degree 3, connects to 2 communities
- [[Roda o pipeline para UM arquivo.      Reuse `engine` quando processar múltiplos]] - degree 3, connects to 2 communities
- [[_validate_request()]] - degree 3, connects to 1 community