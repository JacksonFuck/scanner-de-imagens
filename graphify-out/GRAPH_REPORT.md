# Graph Report - src  (2026-05-02)

## Corpus Check
- 10 files · ~2,825 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 74 nodes · 162 edges · 18 communities detected
- Extraction: 48% EXTRACTED · 52% INFERRED · 0% AMBIGUOUS · INFERRED: 84 edges (avg confidence: 0.55)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]

## God Nodes (most connected - your core abstractions)
1. `InvalidInputError` - 27 edges
2. `DoclingEngine` - 23 edges
3. `ConversionError` - 16 edges
4. `ConfigurationError` - 16 edges
5. `ScannerError` - 12 edges
6. `OutputFormat` - 11 edges
7. `scan_batch()` - 8 edges
8. `ScanResult` - 7 edges
9. `scan()` - 7 edges
10. `Scanner de Imagens — OCR de fotos de páginas para Markdown estruturado + DOCX.` - 7 edges

## Surprising Connections (you probably didn't know these)
- `Engines de extração. Atualmente: Docling (default).` --uses--> `DoclingEngine`  [INFERRED]
  engine\__init__.py → engine\docling_engine.py
- `convert()` --calls--> `collect_inputs()`  [INFERRED]
  cli.py → pipeline.py
- `convert()` --calls--> `scan_batch()`  [INFERRED]
  cli.py → pipeline.py
- `CLI Typer + Rich.  Apresentação fina sobre `pipeline.scan_batch`. Toda lógica de` --uses--> `ScannerError`  [INFERRED]
  cli.py → errors.py
- `CLI Typer + Rich.  Apresentação fina sobre `pipeline.scan_batch`. Toda lógica de` --uses--> `OutputFormat`  [INFERRED]
  cli.py → pipeline.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.43
Nodes (8): DoclingEngine, Wrapper fino do `DocumentConverter` do Docling.      Inicialização cara (carrega, BatchResult, Processa múltiplos arquivos reusando uma única instância do engine.      Quando, Pedido de scan — input + onde gravar + o que produzir., Resultado de um batch (1+ arquivos)., scan_batch(), ScanRequest

### Community 1 - "Community 1"
Cohesion: 0.43
Nodes (7): _ensure_pandoc(), Conversão Markdown → DOCX usando pandoc.  Decisão registrada em `vault/projeto/d, Converte um arquivo Markdown para DOCX preservando imagens e estrutura.      Arg, Garante que pandoc está disponível.      Ordem de busca:     1. PATH do shell (`, write_docx(), ConfigurationError, Configuração inválida (engine não disponível, pandoc faltando, etc.).

### Community 2 - "Community 2"
Cohesion: 0.4
Nodes (4): Orquestrador — costura ingest → engine → exports.  Função pública `scan()` é o p, Roda o pipeline para UM arquivo.      Reuse `engine` quando processar múltiplos, scan(), _validate_request()

### Community 3 - "Community 3"
Cohesion: 0.53
Nodes (5): ExtractionResult, Extrai conteúdo do arquivo `source` para `markdown_target` + imagens em `artifac, Resultado da extração — payload puro, paths para arquivos já gravados.      O Do, ConversionError, Falha durante extração via Docling ou conversão para DOCX.

### Community 4 - "Community 4"
Cohesion: 0.4
Nodes (3): main(), CLI Typer + Rich.  Apresentação fina sobre `pipeline.scan_batch`. Toda lógica de, Configura logging com base nas flags globais.

### Community 5 - "Community 5"
Cohesion: 0.4
Nodes (4): Scanner de Imagens — OCR de fotos de páginas para Markdown estruturado + DOCX., OutputFormat, Formatos de saída solicitáveis., StrEnum

### Community 6 - "Community 6"
Cohesion: 0.5
Nodes (5): Resolve 'auto' para 'cuda' se disponível, senão 'cpu'., InvalidInputError, Input inexistente, formato não suportado ou corrompido., collect_inputs(), Expande um caminho: arquivo único → [arquivo]; pasta → todos os suportados.

### Community 7 - "Community 7"
Cohesion: 0.4
Nodes (3): Adapter para Docling DocumentConverter.  Encapsula toda a interação com a API al, _resolve_device(), _validate_source()

### Community 8 - "Community 8"
Cohesion: 0.5
Nodes (4): convert(), Converte foto(s) de página(s) em Markdown estruturado.      Exemplos:        sca, Imprime tabela Rich com sucessos e falhas., _render_results()

### Community 9 - "Community 9"
Cohesion: 0.5
Nodes (3): Persistência do markdown extraído., Escreve o markdown em `target`, criando pastas pai se necessário.      Returns:, write_markdown()

### Community 10 - "Community 10"
Cohesion: 0.67
Nodes (3): Exception, Erro base do scanner — qualquer falha esperada herda daqui., ScannerError

### Community 11 - "Community 11"
Cohesion: 0.67
Nodes (2): Resultado: caminhos dos arquivos gerados., ScanResult

### Community 12 - "Community 12"
Cohesion: 1.0
Nodes (2): Resolve a flag --merge.      - Se explícito (True/False): usa o valor passado., _resolve_merge()

### Community 13 - "Community 13"
Cohesion: 1.0
Nodes (2): merge_results(), Concatena MDs de múltiplos resultados em um único arquivo.      Cada seção começ

### Community 14 - "Community 14"
Cohesion: 1.0
Nodes (1): Permite invocar o scanner via `python -m scanner`.

### Community 15 - "Community 15"
Cohesion: 1.0
Nodes (1): Exceções específicas do scanner.  Hierarquia simples: tudo herda de `ScannerErro

### Community 16 - "Community 16"
Cohesion: 1.0
Nodes (1): Engines de extração. Atualmente: Docling (default).

### Community 17 - "Community 17"
Cohesion: 1.0
Nodes (1): Exporters — escrevem o resultado da extração em formatos finais.

## Knowledge Gaps
- **9 isolated node(s):** `Exceções específicas do scanner.  Hierarquia simples: tudo herda de `ScannerErro`, `Erro base do scanner — qualquer falha esperada herda daqui.`, `Input inexistente, formato não suportado ou corrompido.`, `Falha durante extração via Docling ou conversão para DOCX.`, `Configuração inválida (engine não disponível, pandoc faltando, etc.).` (+4 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 11`** (3 nodes): `Resultado: caminhos dos arquivos gerados.`, `ScanResult`, `.__str__()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 12`** (2 nodes): `Resolve a flag --merge.      - Se explícito (True/False): usa o valor passado.`, `_resolve_merge()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 13`** (2 nodes): `merge_results()`, `Concatena MDs de múltiplos resultados em um único arquivo.      Cada seção começ`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 14`** (2 nodes): `__main__.py`, `Permite invocar o scanner via `python -m scanner`.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 15`** (2 nodes): `errors.py`, `Exceções específicas do scanner.  Hierarquia simples: tudo herda de `ScannerErro`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 16`** (2 nodes): `__init__.py`, `Engines de extração. Atualmente: Docling (default).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 17`** (2 nodes): `__init__.py`, `Exporters — escrevem o resultado da extração em formatos finais.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `InvalidInputError` connect `Community 6` to `Community 0`, `Community 2`, `Community 3`, `Community 5`, `Community 7`, `Community 10`, `Community 11`, `Community 13`, `Community 15`?**
  _High betweenness centrality (0.213) - this node is a cross-community bridge._
- **Why does `DoclingEngine` connect `Community 0` to `Community 1`, `Community 2`, `Community 3`, `Community 5`, `Community 6`, `Community 7`, `Community 11`, `Community 13`, `Community 16`?**
  _High betweenness centrality (0.205) - this node is a cross-community bridge._
- **Why does `ScannerError` connect `Community 10` to `Community 1`, `Community 3`, `Community 4`, `Community 5`, `Community 6`, `Community 8`, `Community 12`, `Community 15`?**
  _High betweenness centrality (0.142) - this node is a cross-community bridge._
- **Are the 24 inferred relationships involving `InvalidInputError` (e.g. with `OutputFormat` and `ScanRequest`) actually correct?**
  _`InvalidInputError` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `DoclingEngine` (e.g. with `OutputFormat` and `ScanRequest`) actually correct?**
  _`DoclingEngine` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `ConversionError` (e.g. with `Scanner de Imagens — OCR de fotos de páginas para Markdown estruturado + DOCX.` and `ExtractionResult`) actually correct?**
  _`ConversionError` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `ConfigurationError` (e.g. with `ExtractionResult` and `DoclingEngine`) actually correct?**
  _`ConfigurationError` has 13 INFERRED edges - model-reasoned connections that need verification._