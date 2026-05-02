---
type: community
cohesion: 0.67
members: 3
---

# Scan Result Model

**Cohesion:** 0.67 - moderately connected
**Members:** 3 nodes

## Members
- [[.__str__()]] - code - pipeline.py
- [[Resultado caminhos dos arquivos gerados.]] - rationale - pipeline.py
- [[ScanResult]] - code - pipeline.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Scan_Result_Model
SORT file.name ASC
```

## Connections to other communities
- 2 edges to [[_COMMUNITY_Input Validation]]
- 2 edges to [[_COMMUNITY_Pipeline Orchestrator]]
- 2 edges to [[_COMMUNITY_Engine + Scan Models]]
- 1 edge to [[_COMMUNITY_CLI Layer]]

## Top bridge nodes
- [[ScanResult]] - degree 7, connects to 4 communities
- [[Resultado caminhos dos arquivos gerados.]] - degree 3, connects to 2 communities