---
source_file: "pipeline.py"
type: "rationale"
community: "Input Validation"
location: "L136"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/Input_Validation
---

# Expande um caminho: arquivo único → [arquivo]; pasta → todos os suportados.

## Connections
- [[DoclingEngine]] - `uses` [INFERRED]
- [[InvalidInputError]] - `uses` [INFERRED]
- [[collect_inputs()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/INFERRED #community/Input_Validation