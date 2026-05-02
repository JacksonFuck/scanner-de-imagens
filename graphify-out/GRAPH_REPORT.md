# Graph Report - ./src  (2026-05-02)

## Corpus Check
- Corpus is ~1,771 words - fits in a single context window. You may not need a graph.

## Summary
- 68 nodes · 147 edges · 13 communities detected
- Extraction: 48% EXTRACTED · 52% INFERRED · 0% AMBIGUOUS · INFERRED: 77 edges (avg confidence: 0.55)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_CLI Layer|CLI Layer]]
- [[_COMMUNITY_DOCX Export|DOCX Export]]
- [[_COMMUNITY_Extraction Output|Extraction Output]]
- [[_COMMUNITY_Engine + Scan Models|Engine + Scan Models]]
- [[_COMMUNITY_Pipeline Orchestrator|Pipeline Orchestrator]]
- [[_COMMUNITY_Input Validation|Input Validation]]
- [[_COMMUNITY_Markdown Export|Markdown Export]]
- [[_COMMUNITY_Docling Adapter|Docling Adapter]]
- [[_COMMUNITY_Scan Result Model|Scan Result Model]]
- [[_COMMUNITY_Error Hierarchy|Error Hierarchy]]
- [[_COMMUNITY_Engine Package|Engine Package]]
- [[_COMMUNITY_Module Entry Point|Module Entry Point]]
- [[_COMMUNITY_Export Package|Export Package]]

## God Nodes (most connected - your core abstractions)
1. `InvalidInputError` - 25 edges
2. `DoclingEngine` - 22 edges
3. `ConversionError` - 15 edges
4. `ConfigurationError` - 15 edges
5. `ScannerError` - 11 edges
6. `OutputFormat` - 10 edges
7. `scan()` - 8 edges
8. `ScanResult` - 7 edges
9. `scan_batch()` - 7 edges
10. `Scanner de Imagens — OCR de fotos de páginas para Markdown estruturado + DOCX.` - 7 edges

## Surprising Connections (you probably didn't know these)
- `Engines de extração. Atualmente: Docling (default).` --uses--> `DoclingEngine`  [INFERRED]
  engine\__init__.py → engine\docling_engine.py
- `convert()` --calls--> `collect_inputs()`  [INFERRED]
  cli.py → pipeline.py
- `convert()` --calls--> `scan_batch()`  [INFERRED]
  cli.py → pipeline.py
- `OutputFormat` --uses--> `InvalidInputError`  [INFERRED]
  pipeline.py → errors.py
- `ScanRequest` --uses--> `InvalidInputError`  [INFERRED]
  pipeline.py → errors.py

## Communities

### Community 0 - "CLI Layer"
Cohesion: 0.18
Nodes (14): Exception, convert(), main(), CLI Typer + Rich.  Apresentação fina sobre `pipeline.scan_batch`. Toda lógica de, Imprime tabela Rich com sucessos e falhas., Configura logging com base nas flags globais., Converte foto(s) de página(s) em Markdown estruturado.      Exemplos:        sca, _render_results() (+6 more)

### Community 1 - "DOCX Export"
Cohesion: 0.36
Nodes (7): _ensure_pandoc(), Conversão Markdown → DOCX usando pandoc.  Decisão registrada em `vault/projeto/d, Converte um arquivo Markdown para DOCX preservando imagens e estrutura.      Arg, Garante que pandoc está disponível. Tenta auto-download se necessário., write_docx(), ConfigurationError, Configuração inválida (engine não disponível, pandoc faltando, etc.).

### Community 2 - "Extraction Output"
Cohesion: 0.43
Nodes (6): ExtractionResult, Resultado da extração — payload puro, sem efeitos colaterais., Wrapper fino do `DocumentConverter` do Docling.      Inicialização cara (carrega, Extrai conteúdo do arquivo `source` salvando imagens em `artifacts_dir`., ConversionError, Falha durante extração via Docling ou conversão para DOCX.

### Community 3 - "Engine + Scan Models"
Cohesion: 0.52
Nodes (7): DoclingEngine, BatchResult, Processa múltiplos arquivos reusando uma única instância do engine., Pedido de scan — input + onde gravar + o que produzir., Resultado de um batch (1+ arquivos)., scan_batch(), ScanRequest

### Community 4 - "Pipeline Orchestrator"
Cohesion: 0.4
Nodes (4): Orquestrador — costura ingest → engine → exports.  Função pública `scan()` é o p, Roda o pipeline para UM arquivo.      Reuse `engine` quando processar múltiplos, scan(), _validate_request()

### Community 5 - "Input Validation"
Cohesion: 0.67
Nodes (4): InvalidInputError, Input inexistente, formato não suportado ou corrompido., collect_inputs(), Expande um caminho: arquivo único → [arquivo]; pasta → todos os suportados.

### Community 6 - "Markdown Export"
Cohesion: 0.5
Nodes (3): Persistência do markdown extraído., Escreve o markdown em `target`, criando pastas pai se necessário.      Returns:, write_markdown()

### Community 7 - "Docling Adapter"
Cohesion: 0.67
Nodes (2): Adapter para Docling DocumentConverter.  Encapsula toda a interação com a API al, _validate_source()

### Community 8 - "Scan Result Model"
Cohesion: 0.67
Nodes (2): Resultado: caminhos dos arquivos gerados., ScanResult

### Community 9 - "Error Hierarchy"
Cohesion: 1.0
Nodes (1): Exceções específicas do scanner.  Hierarquia simples: tudo herda de `ScannerErro

### Community 10 - "Engine Package"
Cohesion: 1.0
Nodes (1): Engines de extração. Atualmente: Docling (default).

### Community 11 - "Module Entry Point"
Cohesion: 1.0
Nodes (1): Permite invocar o scanner via `python -m scanner`.

### Community 12 - "Export Package"
Cohesion: 1.0
Nodes (1): Exporters — escrevem o resultado da extração em formatos finais.

## Knowledge Gaps
- **9 isolated node(s):** `Exceções específicas do scanner.  Hierarquia simples: tudo herda de `ScannerErro`, `Erro base do scanner — qualquer falha esperada herda daqui.`, `Input inexistente, formato não suportado ou corrompido.`, `Falha durante extração via Docling ou conversão para DOCX.`, `Configuração inválida (engine não disponível, pandoc faltando, etc.).` (+4 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Docling Adapter`** (3 nodes): `docling_engine.py`, `Adapter para Docling DocumentConverter.  Encapsula toda a interação com a API al`, `_validate_source()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Scan Result Model`** (3 nodes): `Resultado: caminhos dos arquivos gerados.`, `ScanResult`, `.__str__()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Error Hierarchy`** (2 nodes): `errors.py`, `Exceções específicas do scanner.  Hierarquia simples: tudo herda de `ScannerErro`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Engine Package`** (2 nodes): `__init__.py`, `Engines de extração. Atualmente: Docling (default).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Module Entry Point`** (2 nodes): `__main__.py`, `Permite invocar o scanner via `python -m scanner`.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Export Package`** (2 nodes): `__init__.py`, `Exporters — escrevem o resultado da extração em formatos finais.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DoclingEngine` connect `Engine + Scan Models` to `CLI Layer`, `DOCX Export`, `Extraction Output`, `Pipeline Orchestrator`, `Input Validation`, `Docling Adapter`, `Scan Result Model`, `Engine Package`?**
  _High betweenness centrality (0.247) - this node is a cross-community bridge._
- **Why does `InvalidInputError` connect `Input Validation` to `CLI Layer`, `Extraction Output`, `Engine + Scan Models`, `Pipeline Orchestrator`, `Docling Adapter`, `Scan Result Model`, `Error Hierarchy`?**
  _High betweenness centrality (0.222) - this node is a cross-community bridge._
- **Why does `ScannerError` connect `CLI Layer` to `Error Hierarchy`, `Extraction Output`, `Input Validation`, `DOCX Export`?**
  _High betweenness centrality (0.142) - this node is a cross-community bridge._
- **Are the 22 inferred relationships involving `InvalidInputError` (e.g. with `OutputFormat` and `ScanRequest`) actually correct?**
  _`InvalidInputError` has 22 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `DoclingEngine` (e.g. with `OutputFormat` and `ScanRequest`) actually correct?**
  _`DoclingEngine` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `ConversionError` (e.g. with `Scanner de Imagens — OCR de fotos de páginas para Markdown estruturado + DOCX.` and `ExtractionResult`) actually correct?**
  _`ConversionError` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `ConfigurationError` (e.g. with `ExtractionResult` and `DoclingEngine`) actually correct?**
  _`ConfigurationError` has 12 INFERRED edges - model-reasoned connections that need verification._