# Graph Report - Scanner de imagens  (2026-05-02)

## Corpus Check
- 392 files · ~5,870,930 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 4667 nodes · 19987 edges · 60 communities detected
- Extraction: 31% EXTRACTED · 69% INFERRED · 0% AMBIGUOUS · INFERRED: 13879 edges (avg confidence: 0.54)
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
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 70|Community 70]]
- [[_COMMUNITY_Community 71|Community 71]]
- [[_COMMUNITY_Community 104|Community 104]]
- [[_COMMUNITY_Community 105|Community 105]]
- [[_COMMUNITY_Community 106|Community 106]]
- [[_COMMUNITY_Community 107|Community 107]]
- [[_COMMUNITY_Community 108|Community 108]]
- [[_COMMUNITY_Community 109|Community 109]]

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
Nodes (485): DeclarativeDocumentBackend, PaginatedDocumentBackend, DeclarativeDocumentBackend.      A declarative document backend is a backend tha, DeclarativeDocumentBackend.      A declarative document backend is a backend tha, Extract the item marker (number or bullet symbol) and the text of the item., Parse an image macro, extracting its path and attributes.         Syntax: image:, Parses the ASCII into a structured document model., Main function that orchestrates the parsing by yielding components:         titl (+477 more)

### Community 1 - "Community 1"
Cohesion: 0.02
Nodes (417): AbstractDocumentBackend, AbstractDocumentBackend, __init__(), AsciiDocBackend, CsvDocumentBackend, DoclingParseDocumentBackend, # TODO: Take width and height from docling-parse., DoclingParseV2DocumentBackend (+409 more)

### Community 2 - "Community 2"
Cohesion: 0.03
Nodes (308): BaseImageClassificationEngineOptions, BaseObjectDetectionEngineOptions, BaseVlmEngine, BaseVlmEngineOptions, HfVisionModelMixin, Shared HuggingFace helpers for vision inference engine families., Get the label mapping for this model., Shared utility mixin for HF vision model loading and label conversion. (+300 more)

### Community 3 - "Community 3"
Cohesion: 0.01
Nodes (236): PdfPageBackend, BaseLayoutModel, BaseLayoutOptions, BasePageModel, BaseTableStructureModel, BaseVlmModel, BaseVlmPageModel, BasePageElement (+228 more)

### Community 4 - "Community 4"
Cohesion: 0.03
Nodes (255): BaseOcrModel, Check if a value is numeric (int or float)., Transform a pandas DataFrame into a TableData object.          Automatically inf, Extract CSV content from decoded text and convert to DataFrame.          Handles, Load the processor and model from the given artifacts path., AcceleratorDevice, AcceleratorOptions, Devices to run model inference (+247 more)

### Community 5 - "Community 5"
Cohesion: 0.03
Nodes (190): BaseModel, OutputFormat, BatchConcurrencySettings, DebugSettings, InferenceSettings, FileSource, HttpSource, S3Coordinates (+182 more)

### Community 6 - "Community 6"
Cohesion: 0.01
Nodes (237): BaseSettings, AppSettings, async_session_factory(), get_engine(), get_session(), SQLAlchemy 2.0 engine + session factory (async via aiosqlite).  A engine é singl, Singleton: cria a engine ao primeiro uso.      Em testes, limpe via `get_engine., Factory de sessions assíncronas, vinculada à engine singleton. (+229 more)

### Community 7 - "Community 7"
Cohesion: 0.01
Nodes (149): convert(), is_valid(), convert(), __init__(), is_valid(), BaseObjectDetectionEngine, Shared inference-engine utilities., KserveV2Client (+141 more)

### Community 8 - "Community 8"
Cohesion: 0.02
Nodes (136): AnnotatedText, AnnotatedTextList, _clean_unicode(), _collect_parent_format_tags(), _Context, convert(), _dom_distance_between_tags(), _extract_direct_text() (+128 more)

### Community 9 - "Community 9"
Cohesion: 0.02
Nodes (101): BaseItemAndImageEnrichmentModel, BaseModelWithOptions, BasePipeline, _BaseChartExtractionModelGraniteVision, ChartExtractionModelGraniteVision, ChartExtractionModelGraniteVisionV4, download_models(), show_external_plugins_callback() (+93 more)

### Community 10 - "Community 10"
Cohesion: 0.03
Nodes (127): DoclingEngine, Wrapper fino do `DocumentConverter` do Docling.      Inicialização cara (carrega, Engines de extração. Atualmente: Docling (default)., Exception, Conversão Markdown → DOCX usando pandoc.  Decisão registrada em `vault/projeto/d, Converte um arquivo Markdown para DOCX preservando imagens e estrutura.      Arg, Garante que pandoc está disponível.      Ordem de busca:     1. PATH do shell (`, write_docx() (+119 more)

### Community 11 - "Community 11"
Cohesion: 0.02
Nodes (22): ABC, DoclingParsePageBackend, _ImagePageBackend, _close_native_document(), _close_native_page(), ManagedPdfiumPageBackend, Shared page lifecycle for PDFium-backed page backends., supported_formats() (+14 more)

### Community 12 - "Community 12"
Cohesion: 0.05
Nodes (49): BaseImageClassificationEngine, process_document(), run(), HfImageClassificationEngineBase, HfVisionModelMixin, ApiKserveV2ImageClassificationEngine, KServe v2 remote implementation for image-classification models., Run inference on a batch of images against a KServe v2 endpoint. (+41 more)

### Community 13 - "Community 13"
Cohesion: 0.06
Nodes (58): get_converter(), get_md_paths(), test_convert_leading_dash_sequences(), test_convert_valid(), test_e2e_md_conversions(), converter(), _create_vtt_stream(), _process_vtt_doc() (+50 more)

### Community 14 - "Community 14"
Cohesion: 0.06
Nodes (44): _apply_accent(), fix_accents(), fix_spaces_and_punct(), fix_zero_as_o(), merge_into_book(), process_markdown(), Implementação do pós-processador PT-BR (lib).  Movido de `scripts/postprocess_md, Aplica todas as correções e retorna o texto pós-processado. (+36 more)

### Community 15 - "Community 15"
Cohesion: 0.13
Nodes (11): AdvancedPIIObfuscator, _build_gliner_model(), _build_simple_ner_pipeline(), main(), Run NER and return a list of (surface_text, type) to obfuscate., Create a GLiNER model for PII-like entity extraction.      Returns a tuple (mode, PII obfuscator powered by GLiNER with fine-grained labels.      - Uses GLiNER's, Create a Hugging Face token-classification pipeline for NER.      Returns a call (+3 more)

### Community 16 - "Community 16"
Cohesion: 0.11
Nodes (13): _detect_csv(), _detect_html_xhtml(), _detect_mets_gbs(), _detect_office_mime_from_zip(), _guess_from_content(), _mime_from_extension(), supports_pagination(), backend() (+5 more)

### Community 17 - "Community 17"
Cohesion: 0.13
Nodes (22): auto_tags(), build_frontmatter(), ChatFile, collect_inputs(), detect_source(), extract_title(), inject_wikilinks(), list_permanent_titles() (+14 more)

### Community 18 - "Community 18"
Cohesion: 0.17
Nodes (16): _get_current_level(), _get_current_parent(), _is_caption(), _is_list_item(), _is_picture(), _is_section_header(), _is_table_line(), _is_title() (+8 more)

### Community 19 - "Community 19"
Cohesion: 0.22
Nodes (20): _get_backend_from_stream(), _make_multipage_tiff_stream(), _make_png_stream(), test_converter_default_maps_image_to_image_backend(), test_crop_page_image(), test_crop_page_image_scaled(), test_docs_builder_multipage_tiff_counts_frames(), test_docs_builder_uses_image_backend_for_image_stream() (+12 more)

### Community 20 - "Community 20"
Cohesion: 0.2
Nodes (3): MacroHandlerMixin, _nodes_to_text(), _process_nodes()

### Community 21 - "Community 21"
Cohesion: 0.15
Nodes (7): _parse_orientation(), TesseractOcrCliModel, test_rotate_bounding_box(), map_tesseract_script(), parse_tesseract_orientation(), tesseract_box_to_bounding_rectangle(), rotate_bounding_box()

### Community 22 - "Community 22"
Cohesion: 0.12
Nodes (15): Testes do endpoint /api/health., Payload tem todos os campos especificados (Section 7.1)., device é cuda | cpu (não 'auto' — já resolvido em runtime)., Phase 1A não tem worker pool ainda — queue_depth = 0., version é o __version__ do scanner_api., disk_free_gb > 0 num filesystem real., Antes de Alembic upgrade, scanner.db não existe — tamanho = 0., GET /api/health responde 200. (+7 more)

### Community 23 - "Community 23"
Cohesion: 0.28
Nodes (6): _clean_math(), EnvironmentHandlerMixin, _extract_macro_arg(), _extract_verbatim_content(), _parse_table(), _process_nodes()

### Community 24 - "Community 24"
Cohesion: 0.14
Nodes (13): Testes do GET /api/jobs/{job_id}/files/{filename}.  Inclui validação de: - 404 q, Se mesmo nome em outputs/ e inputs/, outputs/ ganha (mais novo)., Job que não existe → 404 (mesmo com filename arbitrário)., Job existe mas arquivo não → 404., Arquivo de input enviado pode ser baixado de volta., Arquivo em outputs/ é encontrado e servido (prioritário sobre inputs)., `..%2Fetc%2Fpasswd` ou similar deve ser rejeitado.      FastAPI/Starlette normal, test_download_404_for_nonexistent_file() (+5 more)

### Community 25 - "Community 25"
Cohesion: 0.18
Nodes (10): crop_whitespace(), get_libreoffice_cmd(), get_pil_from_dml_docx(), Return the libreoffice cmd and optionally test it., converter(), get_pdf_path(), test_convert_no_pipeline_with_exception(), test_convert_no_pipeline_wout_exception() (+2 more)

### Community 26 - "Community 26"
Cohesion: 0.23
Nodes (7): _expand_custom_macro_invocation(), _expand_macros(), _extract_macro_arg(), _parse_latex_fragment_to_text(), _process_nodes(), Return ``(text, consumed_following)`` for a single macro node., TextHelperMixin

### Community 27 - "Community 27"
Cohesion: 0.27
Nodes (9): _collect_annotation_content(), parse_deepseekocr_markdown(), _parse_table_html(), _process_annotation_item(), Utilities for parsing DeepSeek OCR annotated markdown format., Collect content for an annotation.      Args:         lines: All lines from the, Process and add a single annotation item to the document.      Args:         lab, Parse DeepSeek OCR markdown with label[[x1, y1, x2, y2]] format.      This funct (+1 more)

### Community 28 - "Community 28"
Cohesion: 0.33
Nodes (8): _make_input_doc(), _make_input_doc_from_stream(), test_in_doc_from_invalid_buf(), test_in_doc_from_invalid_path(), test_in_doc_from_valid_buf(), test_in_doc_from_valid_path(), test_in_doc_with_page_range(), test_tiff_two_pages()

### Community 29 - "Community 29"
Cohesion: 0.36
Nodes (7): _add_child_elements(), _flatten_table_grid(), Find item in document from a reference path, # TODO: Infer if this is a numbered or a bullet list item, # TODO: Infer if this is a numbered or a bullet list item, resolve_item(), to_docling_document()

### Community 30 - "Community 30"
Cohesion: 0.33
Nodes (5): downgrade(), initial schema (jobs, job_files, push_subscriptions)  Revision ID: 0001 Revises:, Reverte as 3 tabelas (drop em ordem reversa do upgrade)., Cria as 3 tabelas + 3 índices da Phase 1A., upgrade()

### Community 31 - "Community 31"
Cohesion: 0.7
Nodes (2): _expand_macros(), MathHandlerMixin

### Community 32 - "Community 32"
Cohesion: 0.5
Nodes (1): TableHelperMixin

### Community 34 - "Community 34"
Cohesion: 0.83
Nodes (3): _install_backend_import_stubs(), _load_msexcel_backend(), test_find_data_tables_handles_a_filled_last_excel_row()

### Community 35 - "Community 35"
Cohesion: 0.5
Nodes (3): Persistência do markdown extraído., Escreve o markdown em `target`, criando pastas pai se necessário.      Returns:, write_markdown()

### Community 37 - "Community 37"
Cohesion: 1.0
Nodes (1): Scanner de Imagens — FastAPI backend.  Exposes the scanner OCR pipeline as a sin

### Community 38 - "Community 38"
Cohesion: 1.0
Nodes (1): DB layer: SQLAlchemy 2.0 async + SQLite via aiosqlite.

### Community 39 - "Community 39"
Cohesion: 1.0
Nodes (1): HTTP routes — agrupados por área.

### Community 40 - "Community 40"
Cohesion: 1.0
Nodes (1): Adapted from https://github.com/xiilei/dwml/blob/master/dwml/latex_dict.py On 23

### Community 41 - "Community 41"
Cohesion: 1.0
Nodes (1): ParseContext

### Community 42 - "Community 42"
Cohesion: 1.0
Nodes (1): Experimental modules for Docling.  This package contains experimental features t

### Community 43 - "Community 43"
Cohesion: 1.0
Nodes (1): Experimental datamodel modules.

### Community 44 - "Community 44"
Cohesion: 1.0
Nodes (1): Experimental models for Docling.

### Community 45 - "Community 45"
Cohesion: 1.0
Nodes (1): Experimental pipeline modules.

### Community 46 - "Community 46"
Cohesion: 1.0
Nodes (1): Inference engine system for Docling.  This package provides a pluggable inferenc

### Community 47 - "Community 47"
Cohesion: 1.0
Nodes (1): Permite invocar o scanner via `python -m scanner`.

### Community 48 - "Community 48"
Cohesion: 1.0
Nodes (1): Exporters — escrevem o resultado da extração em formatos finais.

### Community 49 - "Community 49"
Cohesion: 1.0
Nodes (1): Pós-processamento de Markdown extraído pelo OCR.  Corrige problemas conhecidos d

### Community 50 - "Community 50"
Cohesion: 1.0
Nodes (1): Caminho do SQLite, sempre dentro do data_dir.

### Community 51 - "Community 51"
Cohesion: 1.0
Nodes (1): Pasta raiz dos jobs (`<data_dir>/jobs/`).

### Community 52 - "Community 52"
Cohesion: 1.0
Nodes (1): SQLAlchemy URL — async driver aiosqlite.

### Community 57 - "Community 57"
Cohesion: 1.0
Nodes (1): Check if a LaTeX string needs wrapping in braces for sub/superscript.

### Community 70 - "Community 70"
Cohesion: 1.0
Nodes (1): r"""         Set num_threads from the "alternative" envvar OMP_NUM_THREADS.

### Community 71 - "Community 71"
Cohesion: 1.0
Nodes (1): Emit deprecation warning if old field name is used during initialization.

### Community 104 - "Community 104"
Cohesion: 1.0
Nodes (1): Factory para criar a app — facilita testes (cria app por test client).

### Community 105 - "Community 105"
Cohesion: 1.0
Nodes (1): Retorna estado do servidor.

### Community 106 - "Community 106"
Cohesion: 1.0
Nodes (1): Cria um data dir temporário e seta env vars necessárias.      SCANNER_VAPID_* sã

### Community 107 - "Community 107"
Cohesion: 1.0
Nodes (1): httpx AsyncClient apontado para a app em ASGI mode.

### Community 108 - "Community 108"
Cohesion: 1.0
Nodes (1): Aplica todas as correções e retorna o texto pós-processado.

### Community 109 - "Community 109"
Cohesion: 1.0
Nodes (1): Concatena MDs num único arquivo com ToC.

## Knowledge Gaps
- **248 isolated node(s):** `FastAPI application — entry point para Uvicorn.  Lifespan async para inicializaç`, `Startup/shutdown hooks.      Phase 1A: apenas log + placeholder. Phase 1B adicio`, `Factory para criar a app — facilita testes (cria app por test client).`, `Pub/sub assíncrono de eventos de progresso de job.  Cada job_id tem um asyncio.E`, `Distribui eventos do .progress.jsonl para clientes WebSocket.` (+243 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 31`** (5 nodes): `math.py`, `_expand_macros()`, `MathHandlerMixin`, `._clean_math()`, `._process_math_node()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (5 nodes): `table.py`, `_nodes_to_text()`, `TableHelperMixin`, `._parse_table()`, `._process_table_macro_node()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 37`** (2 nodes): `__init__.py`, `Scanner de Imagens — FastAPI backend.  Exposes the scanner OCR pipeline as a sin`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (2 nodes): `__init__.py`, `DB layer: SQLAlchemy 2.0 async + SQLite via aiosqlite.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (2 nodes): `__init__.py`, `HTTP routes — agrupados por área.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 40`** (2 nodes): `latex_dict.py`, `Adapted from https://github.com/xiilei/dwml/blob/master/dwml/latex_dict.py On 23`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 41`** (2 nodes): `context.py`, `ParseContext`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 42`** (2 nodes): `__init__.py`, `Experimental modules for Docling.  This package contains experimental features t`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 43`** (2 nodes): `Experimental datamodel modules.`, `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 44`** (2 nodes): `__init__.py`, `Experimental models for Docling.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 45`** (2 nodes): `__init__.py`, `Experimental pipeline modules.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (2 nodes): `__init__.py`, `Inference engine system for Docling.  This package provides a pluggable inferenc`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (2 nodes): `Permite invocar o scanner via `python -m scanner`.`, `__main__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 48`** (2 nodes): `Exporters — escrevem o resultado da extração em formatos finais.`, `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (2 nodes): `Pós-processamento de Markdown extraído pelo OCR.  Corrige problemas conhecidos d`, `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 50`** (1 nodes): `Caminho do SQLite, sempre dentro do data_dir.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 51`** (1 nodes): `Pasta raiz dos jobs (`<data_dir>/jobs/`).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 52`** (1 nodes): `SQLAlchemy URL — async driver aiosqlite.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 57`** (1 nodes): `Check if a LaTeX string needs wrapping in braces for sub/superscript.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 70`** (1 nodes): `r"""         Set num_threads from the "alternative" envvar OMP_NUM_THREADS.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 71`** (1 nodes): `Emit deprecation warning if old field name is used during initialization.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 104`** (1 nodes): `Factory para criar a app — facilita testes (cria app por test client).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 105`** (1 nodes): `Retorna estado do servidor.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 106`** (1 nodes): `Cria um data dir temporário e seta env vars necessárias.      SCANNER_VAPID_* sã`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 107`** (1 nodes): `httpx AsyncClient apontado para a app em ASGI mode.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 108`** (1 nodes): `Aplica todas as correções e retorna o texto pós-processado.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 109`** (1 nodes): `Concatena MDs num único arquivo com ToC.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `InputDocument` connect `Community 0` to `Community 1`, `Community 2`, `Community 3`, `Community 5`, `Community 7`, `Community 8`, `Community 9`, `Community 11`, `Community 13`, `Community 16`, `Community 19`, `Community 28`?**
  _High betweenness centrality (0.147) - this node is a cross-community bridge._
- **Why does `InputFormat` connect `Community 0` to `Community 1`, `Community 2`, `Community 3`, `Community 4`, `Community 5`, `Community 8`, `Community 9`, `Community 10`, `Community 11`, `Community 13`, `Community 15`?**
  _High betweenness centrality (0.116) - this node is a cross-community bridge._
- **Why does `AcceleratorOptions` connect `Community 4` to `Community 1`, `Community 2`, `Community 3`, `Community 6`, `Community 7`, `Community 9`, `Community 10`, `Community 12`, `Community 21`?**
  _High betweenness centrality (0.085) - this node is a cross-community bridge._
- **Are the 590 inferred relationships involving `InputDocument` (e.g. with `FormatOption` and `CsvFormatOption`) actually correct?**
  _`InputDocument` has 590 INFERRED edges - model-reasoned connections that need verification._
- **Are the 560 inferred relationships involving `InputFormat` (e.g. with `FormatOption` and `CsvFormatOption`) actually correct?**
  _`InputFormat` has 560 INFERRED edges - model-reasoned connections that need verification._
- **Are the 393 inferred relationships involving `AcceleratorOptions` (e.g. with `BaseOptions` and `TableFormerMode`) actually correct?**
  _`AcceleratorOptions` has 393 INFERRED edges - model-reasoned connections that need verification._
- **Are the 373 inferred relationships involving `ConversionResult` (e.g. with `FormatOption` and `CsvFormatOption`) actually correct?**
  _`ConversionResult` has 373 INFERRED edges - model-reasoned connections that need verification._