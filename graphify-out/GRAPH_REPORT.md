# Graph Report - Scanner de imagens  (2026-05-02)

## Corpus Check
- 417 files · ~5,880,128 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 4820 nodes · 20333 edges · 75 communities detected
- Extraction: 31% EXTRACTED · 69% INFERRED · 0% AMBIGUOUS · INFERRED: 14097 edges (avg confidence: 0.54)
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
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 65|Community 65]]
- [[_COMMUNITY_Community 66|Community 66]]
- [[_COMMUNITY_Community 67|Community 67]]
- [[_COMMUNITY_Community 78|Community 78]]
- [[_COMMUNITY_Community 91|Community 91]]
- [[_COMMUNITY_Community 92|Community 92]]
- [[_COMMUNITY_Community 125|Community 125]]
- [[_COMMUNITY_Community 126|Community 126]]
- [[_COMMUNITY_Community 127|Community 127]]
- [[_COMMUNITY_Community 128|Community 128]]
- [[_COMMUNITY_Community 129|Community 129]]
- [[_COMMUNITY_Community 130|Community 130]]
- [[_COMMUNITY_Community 131|Community 131]]
- [[_COMMUNITY_Community 132|Community 132]]
- [[_COMMUNITY_Community 133|Community 133]]
- [[_COMMUNITY_Community 134|Community 134]]
- [[_COMMUNITY_Community 135|Community 135]]
- [[_COMMUNITY_Community 136|Community 136]]
- [[_COMMUNITY_Community 137|Community 137]]
- [[_COMMUNITY_Community 138|Community 138]]
- [[_COMMUNITY_Community 139|Community 139]]
- [[_COMMUNITY_Community 140|Community 140]]
- [[_COMMUNITY_Community 141|Community 141]]

## God Nodes (most connected - your core abstractions)
1. `InputDocument` - 596 edges
2. `InputFormat` - 564 edges
3. `AcceleratorOptions` - 396 edges
4. `ConversionResult` - 375 edges
5. `DocumentConverter` - 368 edges
6. `AcceleratorDevice` - 264 edges
7. `Page` - 250 edges
8. `EngineModelConfig` - 240 edges
9. `DeclarativeDocumentBackend` - 235 edges
10. `ResponseFormat` - 235 edges

## Surprising Connections (you probably didn't know these)
- `Tudo que o worker precisa para processar (sem ORM).` --uses--> `OutputFormat`  [INFERRED]
  apps\api\src\scanner_api\workers\worker_main.py → src\scanner\pipeline.py
- `DocumentConverter` --calls--> `test_converter_default_maps_image_to_image_backend()`  [INFERRED]
  docling-main\docling-main\docling\document_converter.py → docling-main\docling-main\tests\test_backend_image_native.py
- `DocumentConverter` --calls--> `converter()`  [INFERRED]
  docling-main\docling-main\docling\document_converter.py → docling-main\docling-main\tests\test_backend_vtt.py
- `DocumentConverter` --calls--> `test_convert_no_pipeline_wout_exception()`  [INFERRED]
  docling-main\docling-main\docling\document_converter.py → docling-main\docling-main\tests\test_invalid_input.py
- `DocumentConverter` --calls--> `test_convert_no_pipeline_with_exception()`  [INFERRED]
  docling-main\docling-main\docling\document_converter.py → docling-main\docling-main\tests\test_invalid_input.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.01
Nodes (519): DeclarativeDocumentBackend, PaginatedDocumentBackend, DeclarativeDocumentBackend.      A declarative document backend is a backend tha, DeclarativeDocumentBackend.      A declarative document backend is a backend tha, Extract the item marker (number or bullet symbol) and the text of the item., Parse an image macro, extracting its path and attributes.         Syntax: image:, Parses the ASCII into a structured document model., Main function that orchestrates the parsing by yielding components:         titl (+511 more)

### Community 1 - "Community 1"
Cohesion: 0.01
Nodes (410): ABC, AbstractDocumentBackend, AbstractDocumentBackend, __init__(), AsciiDocBackend, CsvDocumentBackend, DoclingParseDocumentBackend, # TODO: Take width and height from docling-parse. (+402 more)

### Community 2 - "Community 2"
Cohesion: 0.01
Nodes (298): PdfDocumentBackend, BaseLayoutModel, BaseLayoutOptions, BaseModelWithOptions, BaseOcrModel, BasePageModel, BaseTableStructureModel, BaseVlmModel (+290 more)

### Community 3 - "Community 3"
Cohesion: 0.04
Nodes (336): BaseImageClassificationEngineOptions, BaseObjectDetectionEngineOptions, BaseVlmEngineOptions, _BaseChartExtractionModelGraniteVision, Check if a value is numeric (int or float)., Transform a pandas DataFrame into a TableData object.          Automatically inf, AcceleratorDevice, Devices to run model inference (+328 more)

### Community 4 - "Community 4"
Cohesion: 0.01
Nodes (248): BaseImageClassificationEngine, BaseItemAndImageEnrichmentModel, BaseObjectDetectionEngine, BaseVlmEngine, ChartExtractionModelGraniteVision, ChartExtractionModelGraniteVisionV4, download_models(), Extract CSV content from decoded text and convert to DataFrame.          Handles (+240 more)

### Community 5 - "Community 5"
Cohesion: 0.01
Nodes (287): async_session_factory(), get_engine(), get_session(), SQLAlchemy 2.0 engine + session factory (async via aiosqlite).  A engine é singl, Singleton: cria a engine ao primeiro uso.      Em testes, limpe via `get_engine., Factory de sessions assíncronas, vinculada à engine singleton., FastAPI dependency: cede uma session por request, encerra ao fim.      Uso em ro, Base (+279 more)

### Community 6 - "Community 6"
Cohesion: 0.03
Nodes (192): BaseModel, OutputFormat, BatchConcurrencySettings, DebugSettings, InferenceSettings, FileSource, HttpSource, S3Coordinates (+184 more)

### Community 7 - "Community 7"
Cohesion: 0.01
Nodes (131): convert(), is_valid(), supported_formats(), convert(), __init__(), is_valid(), Shared inference-engine utilities., KserveV2Client (+123 more)

### Community 8 - "Community 8"
Cohesion: 0.02
Nodes (116): AnnotatedText, AnnotatedTextList, _clean_unicode(), _collect_parent_format_tags(), convert(), _dom_distance_between_tags(), _extract_direct_text(), _extract_form_marker_text() (+108 more)

### Community 9 - "Community 9"
Cohesion: 0.03
Nodes (134): DoclingEngine, ExtractionResult, Extrai conteúdo do arquivo `source` para `markdown_target` + imagens em `artifac, Resultado da extração — payload puro, paths para arquivos já gravados.      O Do, Wrapper fino do `DocumentConverter` do Docling.      Inicialização cara (carrega, _resolve_device(), _validate_source(), Engines de extração. Atualmente: Docling (default). (+126 more)

### Community 10 - "Community 10"
Cohesion: 0.04
Nodes (85): get_converter(), get_csv_path(), get_csv_paths(), Regression test: converting an empty CSV file should not raise an IndexError., test_e2e_invalid_csv_conversions(), test_e2e_valid_csv_conversions(), test_empty_csv(), get_converter() (+77 more)

### Community 11 - "Community 11"
Cohesion: 0.04
Nodes (47): BasePipeline, _label_value(), _meets_confidence(), _passes_classification(), PictureDescriptionBaseModel, # FIXME: annotations is deprecated, remove once all consumers use meta.classific, PictureDescriptionApiModel, PictureDescriptionVlmModel (+39 more)

### Community 12 - "Community 12"
Cohesion: 0.05
Nodes (22): convert(), _get_format_from_run(), _group_cell_elements(), __init__(), is_valid(), _isolated_list_context(), load_msword_file(), MsWordDocumentBackend (+14 more)

### Community 13 - "Community 13"
Cohesion: 0.05
Nodes (43): _AvailableModels, download(), download_hf_repo(), TableStructureFactory, download_models(), download_models_hf(), get_default_options(), download_models() (+35 more)

### Community 14 - "Community 14"
Cohesion: 0.06
Nodes (44): _apply_accent(), fix_accents(), fix_spaces_and_punct(), fix_zero_as_o(), merge_into_book(), process_markdown(), Implementação do pós-processador PT-BR (lib).  Movido de `scripts/postprocess_md, Aplica todas as correções e retorna o texto pós-processado. (+36 more)

### Community 15 - "Community 15"
Cohesion: 0.07
Nodes (20): _detect_csv(), _detect_html_xhtml(), _detect_mets_gbs(), _detect_office_mime_from_zip(), _guess_from_content(), _mime_from_extension(), supports_pagination(), BaseError (+12 more)

### Community 16 - "Community 16"
Cohesion: 0.12
Nodes (4): DoclingParsePageBackend, get_pdf_page_geometry(), PyPdfiumPageBackend, ManagedPdfiumPageBackend

### Community 17 - "Community 17"
Cohesion: 0.11
Nodes (20): get_broker(), ProgressBroker, Pub/sub assíncrono de eventos de progresso de job.  Cada job_id tem um asyncio.E, Distribui eventos do .progress.jsonl para clientes WebSocket., Sinaliza que novos eventos foram escritos no .progress.jsonl.          Como o ar, Yields cada nova linha do .progress.jsonl como dict.          Termina quando apa, Retorna a instância singleton do ProgressBroker., Testes do ProgressBroker — pub/sub via .progress.jsonl. (+12 more)

### Community 18 - "Community 18"
Cohesion: 0.1
Nodes (3): _ImagePageBackend, MetsGbsPageBackend, PdfPageBackend

### Community 19 - "Community 19"
Cohesion: 0.13
Nodes (11): AdvancedPIIObfuscator, _build_gliner_model(), _build_simple_ner_pipeline(), main(), Run NER and return a list of (surface_text, type) to obfuscate., Create a GLiNER model for PII-like entity extraction.      Returns a tuple (mode, PII obfuscator powered by GLiNER with fine-grained labels.      - Uses GLiNER's, Create a Hugging Face token-classification pipeline for NER.      Returns a call (+3 more)

### Community 20 - "Community 20"
Cohesion: 0.13
Nodes (22): auto_tags(), build_frontmatter(), ChatFile, collect_inputs(), detect_source(), extract_title(), inject_wikilinks(), list_permanent_titles() (+14 more)

### Community 21 - "Community 21"
Cohesion: 0.17
Nodes (16): _get_current_level(), _get_current_parent(), _is_caption(), _is_list_item(), _is_picture(), _is_section_header(), _is_table_line(), _is_title() (+8 more)

### Community 22 - "Community 22"
Cohesion: 0.2
Nodes (3): MacroHandlerMixin, _nodes_to_text(), _process_nodes()

### Community 23 - "Community 23"
Cohesion: 0.11
Nodes (17): Testes do endpoint /api/health., Payload tem todos os campos especificados (Section 7.1)., device é cuda | cpu (não 'auto' — já resolvido em runtime)., Phase 1A não tem worker pool ainda — queue_depth = 0., version é o __version__ do scanner_api., disk_free_gb > 0 num filesystem real., Schema recém-criado (Base.metadata.create_all em conftest) é pequeno     mas não, DB recém-criado: 0 jobs expirados e 0 subscriptions. (+9 more)

### Community 24 - "Community 24"
Cohesion: 0.28
Nodes (6): _clean_math(), EnvironmentHandlerMixin, _extract_macro_arg(), _extract_verbatim_content(), _parse_table(), _process_nodes()

### Community 26 - "Community 26"
Cohesion: 0.14
Nodes (13): Testes do GET /api/jobs/{job_id}/files/{filename}.  Inclui validação de: - 404 q, Se mesmo nome em outputs/ e inputs/, outputs/ ganha (mais novo)., Job que não existe → 404 (mesmo com filename arbitrário)., Job existe mas arquivo não → 404., Arquivo de input enviado pode ser baixado de volta., Arquivo em outputs/ é encontrado e servido (prioritário sobre inputs)., `..%2Fetc%2Fpasswd` ou similar deve ser rejeitado.      FastAPI/Starlette normal, test_download_404_for_nonexistent_file() (+5 more)

### Community 27 - "Community 27"
Cohesion: 0.23
Nodes (7): _expand_custom_macro_invocation(), _expand_macros(), _extract_macro_arg(), _parse_latex_fragment_to_text(), _process_nodes(), Return ``(text, consumed_following)`` for a single macro node., TextHelperMixin

### Community 28 - "Community 28"
Cohesion: 0.27
Nodes (9): _collect_annotation_content(), parse_deepseekocr_markdown(), _parse_table_html(), _process_annotation_item(), Utilities for parsing DeepSeek OCR annotated markdown format., Collect content for an annotation.      Args:         lines: All lines from the, Process and add a single annotation item to the document.      Args:         lab, Parse DeepSeek OCR markdown with label[[x1, y1, x2, y2]] format.      This funct (+1 more)

### Community 29 - "Community 29"
Cohesion: 0.36
Nodes (6): createJob(), getHealth(), getJob(), jsonOrThrow(), listJobs(), patchJob()

### Community 30 - "Community 30"
Cohesion: 0.36
Nodes (7): _add_child_elements(), _flatten_table_grid(), Find item in document from a reference path, # TODO: Infer if this is a numbered or a bullet list item, # TODO: Infer if this is a numbered or a bullet list item, resolve_item(), to_docling_document()

### Community 31 - "Community 31"
Cohesion: 0.33
Nodes (5): downgrade(), initial schema (jobs, job_files, push_subscriptions)  Revision ID: 0001 Revises:, Reverte as 3 tabelas (drop em ordem reversa do upgrade)., Cria as 3 tabelas + 3 índices da Phase 1A., upgrade()

### Community 32 - "Community 32"
Cohesion: 0.7
Nodes (2): _expand_macros(), MathHandlerMixin

### Community 33 - "Community 33"
Cohesion: 0.5
Nodes (1): TableHelperMixin

### Community 35 - "Community 35"
Cohesion: 0.5
Nodes (4): _b64url(), main(), Gera um par de chaves VAPID (base64url) para Web Push.  Uso (uma vez por deploy), base64url sem padding (formato exigido pelo Web Push / VAPID).

### Community 36 - "Community 36"
Cohesion: 0.5
Nodes (1): Common KServe v2 API configuration options mixin.

### Community 37 - "Community 37"
Cohesion: 0.5
Nodes (2): _determine_status(), get_default_options()

### Community 38 - "Community 38"
Cohesion: 0.83
Nodes (3): _install_backend_import_stubs(), _load_msexcel_backend(), test_find_data_tables_handles_a_filled_last_excel_row()

### Community 39 - "Community 39"
Cohesion: 0.5
Nodes (3): Persistência do markdown extraído., Escreve o markdown em `target`, criando pastas pai se necessário.      Returns:, write_markdown()

### Community 43 - "Community 43"
Cohesion: 1.0
Nodes (1): Scanner de Imagens — FastAPI backend.  Exposes the scanner OCR pipeline as a sin

### Community 44 - "Community 44"
Cohesion: 1.0
Nodes (1): DB layer: SQLAlchemy 2.0 async + SQLite via aiosqlite.

### Community 45 - "Community 45"
Cohesion: 1.0
Nodes (1): HTTP routes — agrupados por área.

### Community 46 - "Community 46"
Cohesion: 1.0
Nodes (1): Standalone tasks (CLIs) — não fazem parte da app HTTP.  Cada módulo tem `__main_

### Community 55 - "Community 55"
Cohesion: 1.0
Nodes (1): Adapted from https://github.com/xiilei/dwml/blob/master/dwml/latex_dict.py On 23

### Community 56 - "Community 56"
Cohesion: 1.0
Nodes (1): ParseContext

### Community 57 - "Community 57"
Cohesion: 1.0
Nodes (1): Experimental modules for Docling.  This package contains experimental features t

### Community 58 - "Community 58"
Cohesion: 1.0
Nodes (1): Experimental datamodel modules.

### Community 59 - "Community 59"
Cohesion: 1.0
Nodes (1): Experimental models for Docling.

### Community 60 - "Community 60"
Cohesion: 1.0
Nodes (1): Experimental pipeline modules.

### Community 61 - "Community 61"
Cohesion: 1.0
Nodes (1): Inference engine system for Docling.  This package provides a pluggable inferenc

### Community 62 - "Community 62"
Cohesion: 1.0
Nodes (1): Permite invocar o scanner via `python -m scanner`.

### Community 63 - "Community 63"
Cohesion: 1.0
Nodes (1): Exporters — escrevem o resultado da extração em formatos finais.

### Community 64 - "Community 64"
Cohesion: 1.0
Nodes (1): Pós-processamento de Markdown extraído pelo OCR.  Corrige problemas conhecidos d

### Community 65 - "Community 65"
Cohesion: 1.0
Nodes (1): Caminho do SQLite, sempre dentro do data_dir.

### Community 66 - "Community 66"
Cohesion: 1.0
Nodes (1): Pasta raiz dos jobs (`<data_dir>/jobs/`).

### Community 67 - "Community 67"
Cohesion: 1.0
Nodes (1): SQLAlchemy URL — async driver aiosqlite.

### Community 78 - "Community 78"
Cohesion: 1.0
Nodes (1): Check if a LaTeX string needs wrapping in braces for sub/superscript.

### Community 91 - "Community 91"
Cohesion: 1.0
Nodes (1): r"""         Set num_threads from the "alternative" envvar OMP_NUM_THREADS.

### Community 92 - "Community 92"
Cohesion: 1.0
Nodes (1): Emit deprecation warning if old field name is used during initialization.

### Community 125 - "Community 125"
Cohesion: 1.0
Nodes (1): Payload do /api/health (espelha spec Section 7.1).

### Community 126 - "Community 126"
Cohesion: 1.0
Nodes (1): Detecta device atual (CUDA disponível? GPU name?).      Honra `settings.device`:

### Community 127 - "Community 127"
Cohesion: 1.0
Nodes (1): Tamanho do arquivo SQLite em MB. 0 se não existe ainda.

### Community 128 - "Community 128"
Cohesion: 1.0
Nodes (1): Espaço livre no filesystem do data_dir, em GB.      Se o data_dir ainda não exis

### Community 129 - "Community 129"
Cohesion: 1.0
Nodes (1): Retorna (queue_depth, workers_busy) do pool, ou (0, 0) se off.      Em testes ou

### Community 130 - "Community 130"
Cohesion: 1.0
Nodes (1): Retorna estado do servidor.

### Community 131 - "Community 131"
Cohesion: 1.0
Nodes (1): device é cuda | cpu (não 'auto' — já resolvido em runtime).

### Community 132 - "Community 132"
Cohesion: 1.0
Nodes (1): Phase 1A não tem worker pool ainda — queue_depth = 0.

### Community 133 - "Community 133"
Cohesion: 1.0
Nodes (1): version é o __version__ do scanner_api.

### Community 134 - "Community 134"
Cohesion: 1.0
Nodes (1): disk_free_gb > 0 num filesystem real.

### Community 135 - "Community 135"
Cohesion: 1.0
Nodes (1): Antes de Alembic upgrade, scanner.db não existe — tamanho = 0.

### Community 136 - "Community 136"
Cohesion: 1.0
Nodes (1): Factory para criar a app — facilita testes (cria app por test client).

### Community 137 - "Community 137"
Cohesion: 1.0
Nodes (1): Retorna estado do servidor.

### Community 138 - "Community 138"
Cohesion: 1.0
Nodes (1): Cria um data dir temporário e seta env vars necessárias.      SCANNER_VAPID_* sã

### Community 139 - "Community 139"
Cohesion: 1.0
Nodes (1): httpx AsyncClient apontado para a app em ASGI mode.

### Community 140 - "Community 140"
Cohesion: 1.0
Nodes (1): Aplica todas as correções e retorna o texto pós-processado.

### Community 141 - "Community 141"
Cohesion: 1.0
Nodes (1): Concatena MDs num único arquivo com ToC.

## Knowledge Gaps
- **269 isolated node(s):** `FastAPI application — entry point para Uvicorn.  Lifespan async para inicializaç`, `Startup/shutdown hooks.      Phase 1A: apenas log + placeholder. Phase 1B adicio`, `Factory para criar a app — facilita testes (cria app por test client).`, `Pub/sub assíncrono de eventos de progresso de job.  Cada job_id tem um asyncio.E`, `Distribui eventos do .progress.jsonl para clientes WebSocket.` (+264 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 32`** (5 nodes): `math.py`, `_expand_macros()`, `MathHandlerMixin`, `._clean_math()`, `._process_math_node()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 33`** (5 nodes): `table.py`, `_nodes_to_text()`, `TableHelperMixin`, `._parse_table()`, `._process_table_macro_node()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (4 nodes): `grpc_use_binary_data()`, `Common KServe v2 API configuration options mixin.`, `_warn_deprecated_alias()`, `kserve_v2_options.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 37`** (4 nodes): `vlm_pipeline.py`, `_determine_status()`, `get_default_options()`, `is_backend_supported()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 43`** (2 nodes): `__init__.py`, `Scanner de Imagens — FastAPI backend.  Exposes the scanner OCR pipeline as a sin`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 44`** (2 nodes): `__init__.py`, `DB layer: SQLAlchemy 2.0 async + SQLite via aiosqlite.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 45`** (2 nodes): `__init__.py`, `HTTP routes — agrupados por área.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (2 nodes): `__init__.py`, `Standalone tasks (CLIs) — não fazem parte da app HTTP.  Cada módulo tem `__main_`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 55`** (2 nodes): `latex_dict.py`, `Adapted from https://github.com/xiilei/dwml/blob/master/dwml/latex_dict.py On 23`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 56`** (2 nodes): `context.py`, `ParseContext`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 57`** (2 nodes): `__init__.py`, `Experimental modules for Docling.  This package contains experimental features t`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 58`** (2 nodes): `Experimental datamodel modules.`, `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 59`** (2 nodes): `__init__.py`, `Experimental models for Docling.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 60`** (2 nodes): `__init__.py`, `Experimental pipeline modules.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 61`** (2 nodes): `__init__.py`, `Inference engine system for Docling.  This package provides a pluggable inferenc`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 62`** (2 nodes): `Permite invocar o scanner via `python -m scanner`.`, `__main__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 63`** (2 nodes): `Exporters — escrevem o resultado da extração em formatos finais.`, `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 64`** (2 nodes): `Pós-processamento de Markdown extraído pelo OCR.  Corrige problemas conhecidos d`, `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 65`** (1 nodes): `Caminho do SQLite, sempre dentro do data_dir.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 66`** (1 nodes): `Pasta raiz dos jobs (`<data_dir>/jobs/`).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 67`** (1 nodes): `SQLAlchemy URL — async driver aiosqlite.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 78`** (1 nodes): `Check if a LaTeX string needs wrapping in braces for sub/superscript.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 91`** (1 nodes): `r"""         Set num_threads from the "alternative" envvar OMP_NUM_THREADS.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 92`** (1 nodes): `Emit deprecation warning if old field name is used during initialization.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 125`** (1 nodes): `Payload do /api/health (espelha spec Section 7.1).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 126`** (1 nodes): `Detecta device atual (CUDA disponível? GPU name?).      Honra `settings.device`:`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 127`** (1 nodes): `Tamanho do arquivo SQLite em MB. 0 se não existe ainda.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 128`** (1 nodes): `Espaço livre no filesystem do data_dir, em GB.      Se o data_dir ainda não exis`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 129`** (1 nodes): `Retorna (queue_depth, workers_busy) do pool, ou (0, 0) se off.      Em testes ou`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 130`** (1 nodes): `Retorna estado do servidor.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 131`** (1 nodes): `device é cuda | cpu (não 'auto' — já resolvido em runtime).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 132`** (1 nodes): `Phase 1A não tem worker pool ainda — queue_depth = 0.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 133`** (1 nodes): `version é o __version__ do scanner_api.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 134`** (1 nodes): `disk_free_gb > 0 num filesystem real.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 135`** (1 nodes): `Antes de Alembic upgrade, scanner.db não existe — tamanho = 0.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 136`** (1 nodes): `Factory para criar a app — facilita testes (cria app por test client).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 137`** (1 nodes): `Retorna estado do servidor.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 138`** (1 nodes): `Cria um data dir temporário e seta env vars necessárias.      SCANNER_VAPID_* sã`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 139`** (1 nodes): `httpx AsyncClient apontado para a app em ASGI mode.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 140`** (1 nodes): `Aplica todas as correções e retorna o texto pós-processado.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 141`** (1 nodes): `Concatena MDs num único arquivo com ToC.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `InputDocument` connect `Community 0` to `Community 1`, `Community 2`, `Community 4`, `Community 6`, `Community 7`, `Community 8`, `Community 10`, `Community 12`, `Community 15`, `Community 16`, `Community 18`?**
  _High betweenness centrality (0.178) - this node is a cross-community bridge._
- **Why does `InputFormat` connect `Community 0` to `Community 1`, `Community 2`, `Community 3`, `Community 4`, `Community 6`, `Community 8`, `Community 9`, `Community 10`, `Community 12`, `Community 18`, `Community 19`?**
  _High betweenness centrality (0.114) - this node is a cross-community bridge._
- **Why does `AcceleratorOptions` connect `Community 4` to `Community 1`, `Community 2`, `Community 3`, `Community 7`, `Community 8`, `Community 9`, `Community 11`, `Community 12`, `Community 13`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Are the 590 inferred relationships involving `InputDocument` (e.g. with `FormatOption` and `CsvFormatOption`) actually correct?**
  _`InputDocument` has 590 INFERRED edges - model-reasoned connections that need verification._
- **Are the 560 inferred relationships involving `InputFormat` (e.g. with `FormatOption` and `CsvFormatOption`) actually correct?**
  _`InputFormat` has 560 INFERRED edges - model-reasoned connections that need verification._
- **Are the 393 inferred relationships involving `AcceleratorOptions` (e.g. with `BaseOptions` and `TableFormerMode`) actually correct?**
  _`AcceleratorOptions` has 393 INFERRED edges - model-reasoned connections that need verification._
- **Are the 373 inferred relationships involving `ConversionResult` (e.g. with `FormatOption` and `CsvFormatOption`) actually correct?**
  _`ConversionResult` has 373 INFERRED edges - model-reasoned connections that need verification._