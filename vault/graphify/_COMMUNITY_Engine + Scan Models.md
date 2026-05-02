---
type: community
cohesion: 0.52
members: 7
---

# Engine + Scan Models

**Cohesion:** 0.52 - moderately connected
**Members:** 7 nodes

## Members
- [[BatchResult]] - code - pipeline.py
- [[DoclingEngine]] - code - engine\docling_engine.py
- [[Pedido de scan — input + onde gravar + o que produzir.]] - rationale - pipeline.py
- [[Processa múltiplos arquivos reusando uma única instância do engine.]] - rationale - pipeline.py
- [[Resultado de um batch (1+ arquivos).]] - rationale - pipeline.py
- [[ScanRequest]] - code - pipeline.py
- [[scan_batch()]] - code - pipeline.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Engine_+_Scan_Models
SORT file.name ASC
```

## Connections to other communities
- 7 edges to [[_COMMUNITY_Input Validation]]
- 7 edges to [[_COMMUNITY_Pipeline Orchestrator]]
- 4 edges to [[_COMMUNITY_CLI Layer]]
- 3 edges to [[_COMMUNITY_Extraction Output]]
- 2 edges to [[_COMMUNITY_DOCX Export]]
- 2 edges to [[_COMMUNITY_Scan Result Model]]
- 1 edge to [[_COMMUNITY_Docling Adapter]]
- 1 edge to [[_COMMUNITY_Engine Package]]

## Top bridge nodes
- [[DoclingEngine]] - degree 22, connects to 8 communities
- [[ScanRequest]] - degree 6, connects to 3 communities
- [[scan_batch()]] - degree 7, connects to 2 communities
- [[BatchResult]] - degree 5, connects to 2 communities
- [[Processa múltiplos arquivos reusando uma única instância do engine.]] - degree 3, connects to 1 community