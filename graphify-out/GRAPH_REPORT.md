# Graph Report - Scanner de imagens  (2026-05-02)

## Corpus Check
- 421 files · ~5,883,284 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 4833 nodes · 20343 edges · 75 communities detected
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
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
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
- [[_COMMUNITY_Community 68|Community 68]]
- [[_COMMUNITY_Community 69|Community 69]]
- [[_COMMUNITY_Community 70|Community 70]]
- [[_COMMUNITY_Community 81|Community 81]]
- [[_COMMUNITY_Community 94|Community 94]]
- [[_COMMUNITY_Community 95|Community 95]]
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
- [[_COMMUNITY_Community 142|Community 142]]
- [[_COMMUNITY_Community 143|Community 143]]
- [[_COMMUNITY_Community 144|Community 144]]

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
Nodes (558): DeclarativeDocumentBackend, PaginatedDocumentBackend, DeclarativeDocumentBackend.      A declarative document backend is a backend tha, DeclarativeDocumentBackend.      A declarative document backend is a backend tha, Extract the item marker (number or bullet symbol) and the text of the item., Parse an image macro, extracting its path and attributes.         Syntax: image:, Parses the ASCII into a structured document model., Main function that orchestrates the parsing by yielding components:         titl (+550 more)

### Community 1 - "Community 1"
Cohesion: 0.01
Nodes (252): BaseLayoutModel, BaseLayoutOptions, BaseModelWithOptions, BasePageModel, BaseTableStructureModel, BaseVlmPageModel, show_external_plugins_callback(), CodeFormulaVlmModel (+244 more)

### Community 2 - "Community 2"
Cohesion: 0.02
Nodes (323): BaseImageClassificationEngineOptions, BaseObjectDetectionEngineOptions, BaseVlmEngine, BaseVlmEngineOptions, HfVisionModelMixin, Shared HuggingFace helpers for vision inference engine families., Get the label mapping for this model., Shared utility mixin for HF vision model loading and label conversion. (+315 more)

### Community 3 - "Community 3"
Cohesion: 0.02
Nodes (256): ABC, AbstractDocumentBackend, __init__(), AsciiDocBackend, CsvDocumentBackend, DoclingParseDocumentBackend, # TODO: Take width and height from docling-parse., DoclingParseV2DocumentBackend (+248 more)

### Community 4 - "Community 4"
Cohesion: 0.03
Nodes (271): BaseItemAndImageEnrichmentModel, BaseOcrModel, _BaseChartExtractionModelGraniteVision, ChartExtractionModelGraniteVision, ChartExtractionModelGraniteVisionV4, download_models(), Check if a value is numeric (int or float)., Transform a pandas DataFrame into a TableData object.          Automatically inf (+263 more)

### Community 5 - "Community 5"
Cohesion: 0.01
Nodes (289): async_session_factory(), get_engine(), get_session(), SQLAlchemy 2.0 engine + session factory (async via aiosqlite).  A engine é singl, Singleton: cria a engine ao primeiro uso.      Em testes, limpe via `get_engine., Factory de sessions assíncronas, vinculada à engine singleton., FastAPI dependency: cede uma session por request, encerra ao fim.      Uso em ro, Base (+281 more)

### Community 6 - "Community 6"
Cohesion: 0.03
Nodes (190): BaseModel, OutputFormat, BatchConcurrencySettings, DebugSettings, InferenceSettings, FileSource, HttpSource, S3Coordinates (+182 more)

### Community 7 - "Community 7"
Cohesion: 0.02
Nodes (119): convert(), __init__(), is_valid(), BaseImageClassificationEngine, Shared inference-engine utilities., KserveV2Client, Shared protocol for KServe v2 transport clients., Transport-agnostic KServe v2 client interface. (+111 more)

### Community 8 - "Community 8"
Cohesion: 0.02
Nodes (135): AnnotatedText, AnnotatedTextList, _clean_unicode(), _collect_parent_format_tags(), convert(), _dom_distance_between_tags(), _extract_direct_text(), _extract_form_marker_text() (+127 more)

### Community 9 - "Community 9"
Cohesion: 0.02
Nodes (116): BaseEnrichmentModel, dict, PdfFormatOption, export_documents(), main(), main(), extract_with_preset(), main() (+108 more)

### Community 10 - "Community 10"
Cohesion: 0.03
Nodes (124): DoclingEngine, Engines de extração. Atualmente: Docling (default)., Exception, Conversão Markdown → DOCX usando pandoc.  Decisão registrada em `vault/projeto/d, Converte um arquivo Markdown para DOCX preservando imagens e estrutura.      Arg, Garante que pandoc está disponível.      Ordem de busca:     1. PATH do shell (`, write_docx(), ensure_pandoc() (+116 more)

### Community 11 - "Community 11"
Cohesion: 0.05
Nodes (93): AbstractDocumentBackend, NoOpBackend, AsrModelType, _get_whisper_base_model(), _get_whisper_large_model(), _get_whisper_medium_model(), _get_whisper_small_model(), _get_whisper_tiny_model() (+85 more)

### Community 12 - "Community 12"
Cohesion: 0.04
Nodes (56): BaseObjectDetectionEngine, _AvailableModels, download(), download_hf_repo(), Helpers for KServe transport URL handling., Resolve runtime base URL for KServe transport clients.      HTTP accepts either, resolve_kserve_transport_base_url(), HfObjectDetectionEngineBase (+48 more)

### Community 13 - "Community 13"
Cohesion: 0.05
Nodes (22): convert(), _get_format_from_run(), _group_cell_elements(), __init__(), is_valid(), _isolated_list_context(), load_msword_file(), MsWordDocumentBackend (+14 more)

### Community 14 - "Community 14"
Cohesion: 0.06
Nodes (59): get_converter(), get_md_paths(), test_convert_leading_dash_sequences(), test_convert_valid(), test_e2e_md_conversions(), converter(), _create_vtt_stream(), _process_vtt_doc() (+51 more)

### Community 15 - "Community 15"
Cohesion: 0.06
Nodes (36): BasePipeline, _label_value(), _meets_confidence(), _passes_classification(), PictureDescriptionBaseModel, PictureDescriptionApiModel, PictureDescriptionBaseModel, PictureDescriptionBaseOptions (+28 more)

### Community 16 - "Community 16"
Cohesion: 0.06
Nodes (44): _apply_accent(), fix_accents(), fix_spaces_and_punct(), fix_zero_as_o(), merge_into_book(), process_markdown(), Implementação do pós-processador PT-BR (lib).  Movido de `scripts/postprocess_md, Aplica todas as correções e retorna o texto pós-processado. (+36 more)

### Community 17 - "Community 17"
Cohesion: 0.12
Nodes (4): DoclingParsePageBackend, get_pdf_page_geometry(), PyPdfiumPageBackend, ManagedPdfiumPageBackend

### Community 18 - "Community 18"
Cohesion: 0.11
Nodes (20): get_broker(), ProgressBroker, Pub/sub assíncrono de eventos de progresso de job.  Cada job_id tem um asyncio.E, Distribui eventos do .progress.jsonl para clientes WebSocket., Sinaliza que novos eventos foram escritos no .progress.jsonl.          Como o ar, Yields cada nova linha do .progress.jsonl como dict.          Termina quando apa, Retorna a instância singleton do ProgressBroker., Testes do ProgressBroker — pub/sub via .progress.jsonl. (+12 more)

### Community 19 - "Community 19"
Cohesion: 0.13
Nodes (22): auto_tags(), build_frontmatter(), ChatFile, collect_inputs(), detect_source(), extract_title(), inject_wikilinks(), list_permanent_titles() (+14 more)

### Community 20 - "Community 20"
Cohesion: 0.17
Nodes (16): _get_current_level(), _get_current_parent(), _is_caption(), _is_list_item(), _is_picture(), _is_section_header(), _is_table_line(), _is_title() (+8 more)

### Community 21 - "Community 21"
Cohesion: 0.2
Nodes (3): MacroHandlerMixin, _nodes_to_text(), _process_nodes()

### Community 22 - "Community 22"
Cohesion: 0.11
Nodes (17): Testes do endpoint /api/health., Payload tem todos os campos especificados (Section 7.1)., device é cuda | cpu (não 'auto' — já resolvido em runtime)., Phase 1A não tem worker pool ainda — queue_depth = 0., version é o __version__ do scanner_api., disk_free_gb > 0 num filesystem real., Schema recém-criado (Base.metadata.create_all em conftest) é pequeno     mas não, DB recém-criado: 0 jobs expirados e 0 subscriptions. (+9 more)

### Community 23 - "Community 23"
Cohesion: 0.28
Nodes (6): _clean_math(), EnvironmentHandlerMixin, _extract_macro_arg(), _extract_verbatim_content(), _parse_table(), _process_nodes()

### Community 25 - "Community 25"
Cohesion: 0.14
Nodes (13): Testes do GET /api/jobs/{job_id}/files/{filename}.  Inclui validação de: - 404 q, Se mesmo nome em outputs/ e inputs/, outputs/ ganha (mais novo)., Job que não existe → 404 (mesmo com filename arbitrário)., Job existe mas arquivo não → 404., Arquivo de input enviado pode ser baixado de volta., Arquivo em outputs/ é encontrado e servido (prioritário sobre inputs)., `..%2Fetc%2Fpasswd` ou similar deve ser rejeitado.      FastAPI/Starlette normal, test_download_404_for_nonexistent_file() (+5 more)

### Community 26 - "Community 26"
Cohesion: 0.23
Nodes (7): _expand_custom_macro_invocation(), _expand_macros(), _extract_macro_arg(), _parse_latex_fragment_to_text(), _process_nodes(), Return ``(text, consumed_following)`` for a single macro node., TextHelperMixin

### Community 27 - "Community 27"
Cohesion: 0.27
Nodes (9): _collect_annotation_content(), parse_deepseekocr_markdown(), _parse_table_html(), _process_annotation_item(), Utilities for parsing DeepSeek OCR annotated markdown format., Collect content for an annotation.      Args:         lines: All lines from the, Process and add a single annotation item to the document.      Args:         lab, Parse DeepSeek OCR markdown with label[[x1, y1, x2, y2]] format.      This funct (+1 more)

### Community 28 - "Community 28"
Cohesion: 0.36
Nodes (6): createJob(), getHealth(), getJob(), jsonOrThrow(), listJobs(), patchJob()

### Community 29 - "Community 29"
Cohesion: 0.22
Nodes (4): DocTagsRepetitionStopper, Detects repetitive <tag>...<loc_x><loc_y><loc_w><loc_h>text</tag> blocks,     bu, 3+ strictly increasing values with ~regular spacing (±20%)., Trip only on **consecutive** runs (no other matched blocks between) of ≥3 items

### Community 30 - "Community 30"
Cohesion: 0.36
Nodes (7): _add_child_elements(), _flatten_table_grid(), Find item in document from a reference path, # TODO: Infer if this is a numbered or a bullet list item, # TODO: Infer if this is a numbered or a bullet list item, resolve_item(), to_docling_document()

### Community 31 - "Community 31"
Cohesion: 0.33
Nodes (5): downgrade(), initial schema (jobs, job_files, push_subscriptions)  Revision ID: 0001 Revises:, Reverte as 3 tabelas (drop em ordem reversa do upgrade)., Cria as 3 tabelas + 3 índices da Phase 1A., upgrade()

### Community 33 - "Community 33"
Cohesion: 0.7
Nodes (2): _expand_macros(), MathHandlerMixin

### Community 34 - "Community 34"
Cohesion: 0.5
Nodes (1): TableHelperMixin

### Community 36 - "Community 36"
Cohesion: 0.5
Nodes (4): _b64url(), main(), Gera um par de chaves VAPID (base64url) para Web Push.  Uso (uma vez por deploy), base64url sem padding (formato exigido pelo Web Push / VAPID).

### Community 37 - "Community 37"
Cohesion: 0.67
Nodes (2): enable(), urlBase64ToUint8Array()

### Community 38 - "Community 38"
Cohesion: 0.67
Nodes (2): _get_backend(), test_asciidocs_examples()

### Community 39 - "Community 39"
Cohesion: 0.83
Nodes (3): _install_backend_import_stubs(), _load_msexcel_backend(), test_find_data_tables_handles_a_filled_last_excel_row()

### Community 40 - "Community 40"
Cohesion: 0.5
Nodes (3): Persistência do markdown extraído., Escreve o markdown em `target`, criando pastas pai se necessário.      Returns:, write_markdown()

### Community 44 - "Community 44"
Cohesion: 1.0
Nodes (1): Scanner de Imagens — FastAPI backend.  Exposes the scanner OCR pipeline as a sin

### Community 45 - "Community 45"
Cohesion: 1.0
Nodes (1): DB layer: SQLAlchemy 2.0 async + SQLite via aiosqlite.

### Community 46 - "Community 46"
Cohesion: 1.0
Nodes (1): HTTP routes — agrupados por área.

### Community 47 - "Community 47"
Cohesion: 1.0
Nodes (1): Standalone tasks (CLIs) — não fazem parte da app HTTP.  Cada módulo tem `__main_

### Community 58 - "Community 58"
Cohesion: 1.0
Nodes (1): Adapted from https://github.com/xiilei/dwml/blob/master/dwml/latex_dict.py On 23

### Community 59 - "Community 59"
Cohesion: 1.0
Nodes (1): ParseContext

### Community 60 - "Community 60"
Cohesion: 1.0
Nodes (1): Experimental modules for Docling.  This package contains experimental features t

### Community 61 - "Community 61"
Cohesion: 1.0
Nodes (1): Experimental datamodel modules.

### Community 62 - "Community 62"
Cohesion: 1.0
Nodes (1): Experimental models for Docling.

### Community 63 - "Community 63"
Cohesion: 1.0
Nodes (1): Experimental pipeline modules.

### Community 64 - "Community 64"
Cohesion: 1.0
Nodes (1): Inference engine system for Docling.  This package provides a pluggable inferenc

### Community 65 - "Community 65"
Cohesion: 1.0
Nodes (1): Permite invocar o scanner via `python -m scanner`.

### Community 66 - "Community 66"
Cohesion: 1.0
Nodes (1): Exporters — escrevem o resultado da extração em formatos finais.

### Community 67 - "Community 67"
Cohesion: 1.0
Nodes (1): Pós-processamento de Markdown extraído pelo OCR.  Corrige problemas conhecidos d

### Community 68 - "Community 68"
Cohesion: 1.0
Nodes (1): Caminho do SQLite, sempre dentro do data_dir.

### Community 69 - "Community 69"
Cohesion: 1.0
Nodes (1): Pasta raiz dos jobs (`<data_dir>/jobs/`).

### Community 70 - "Community 70"
Cohesion: 1.0
Nodes (1): SQLAlchemy URL — async driver aiosqlite.

### Community 81 - "Community 81"
Cohesion: 1.0
Nodes (1): Check if a LaTeX string needs wrapping in braces for sub/superscript.

### Community 94 - "Community 94"
Cohesion: 1.0
Nodes (1): r"""         Set num_threads from the "alternative" envvar OMP_NUM_THREADS.

### Community 95 - "Community 95"
Cohesion: 1.0
Nodes (1): Emit deprecation warning if old field name is used during initialization.

### Community 128 - "Community 128"
Cohesion: 1.0
Nodes (1): Payload do /api/health (espelha spec Section 7.1).

### Community 129 - "Community 129"
Cohesion: 1.0
Nodes (1): Detecta device atual (CUDA disponível? GPU name?).      Honra `settings.device`:

### Community 130 - "Community 130"
Cohesion: 1.0
Nodes (1): Tamanho do arquivo SQLite em MB. 0 se não existe ainda.

### Community 131 - "Community 131"
Cohesion: 1.0
Nodes (1): Espaço livre no filesystem do data_dir, em GB.      Se o data_dir ainda não exis

### Community 132 - "Community 132"
Cohesion: 1.0
Nodes (1): Retorna (queue_depth, workers_busy) do pool, ou (0, 0) se off.      Em testes ou

### Community 133 - "Community 133"
Cohesion: 1.0
Nodes (1): Retorna estado do servidor.

### Community 134 - "Community 134"
Cohesion: 1.0
Nodes (1): device é cuda | cpu (não 'auto' — já resolvido em runtime).

### Community 135 - "Community 135"
Cohesion: 1.0
Nodes (1): Phase 1A não tem worker pool ainda — queue_depth = 0.

### Community 136 - "Community 136"
Cohesion: 1.0
Nodes (1): version é o __version__ do scanner_api.

### Community 137 - "Community 137"
Cohesion: 1.0
Nodes (1): disk_free_gb > 0 num filesystem real.

### Community 138 - "Community 138"
Cohesion: 1.0
Nodes (1): Antes de Alembic upgrade, scanner.db não existe — tamanho = 0.

### Community 139 - "Community 139"
Cohesion: 1.0
Nodes (1): Factory para criar a app — facilita testes (cria app por test client).

### Community 140 - "Community 140"
Cohesion: 1.0
Nodes (1): Retorna estado do servidor.

### Community 141 - "Community 141"
Cohesion: 1.0
Nodes (1): Cria um data dir temporário e seta env vars necessárias.      SCANNER_VAPID_* sã

### Community 142 - "Community 142"
Cohesion: 1.0
Nodes (1): httpx AsyncClient apontado para a app em ASGI mode.

### Community 143 - "Community 143"
Cohesion: 1.0
Nodes (1): Aplica todas as correções e retorna o texto pós-processado.

### Community 144 - "Community 144"
Cohesion: 1.0
Nodes (1): Concatena MDs num único arquivo com ToC.

## Knowledge Gaps
- **269 isolated node(s):** `FastAPI application — entry point para Uvicorn.  Lifespan async para inicializaç`, `Startup/shutdown hooks.      Phase 1A: apenas log + placeholder. Phase 1B adicio`, `Factory para criar a app — facilita testes (cria app por test client).`, `Pub/sub assíncrono de eventos de progresso de job.  Cada job_id tem um asyncio.E`, `Distribui eventos do .progress.jsonl para clientes WebSocket.` (+264 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 33`** (5 nodes): `math.py`, `_expand_macros()`, `MathHandlerMixin`, `._clean_math()`, `._process_math_node()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (5 nodes): `table.py`, `_nodes_to_text()`, `TableHelperMixin`, `._parse_table()`, `._process_table_macro_node()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 37`** (4 nodes): `EnablePush.tsx`, `disable()`, `enable()`, `urlBase64ToUint8Array()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (4 nodes): `test_backend_asciidoc.py`, `_get_backend()`, `test_asciidocs_examples()`, `test_parse_picture()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 44`** (2 nodes): `__init__.py`, `Scanner de Imagens — FastAPI backend.  Exposes the scanner OCR pipeline as a sin`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 45`** (2 nodes): `__init__.py`, `DB layer: SQLAlchemy 2.0 async + SQLite via aiosqlite.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (2 nodes): `__init__.py`, `HTTP routes — agrupados por área.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (2 nodes): `__init__.py`, `Standalone tasks (CLIs) — não fazem parte da app HTTP.  Cada módulo tem `__main_`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 58`** (2 nodes): `latex_dict.py`, `Adapted from https://github.com/xiilei/dwml/blob/master/dwml/latex_dict.py On 23`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 59`** (2 nodes): `context.py`, `ParseContext`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 60`** (2 nodes): `__init__.py`, `Experimental modules for Docling.  This package contains experimental features t`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 61`** (2 nodes): `Experimental datamodel modules.`, `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 62`** (2 nodes): `__init__.py`, `Experimental models for Docling.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 63`** (2 nodes): `__init__.py`, `Experimental pipeline modules.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 64`** (2 nodes): `__init__.py`, `Inference engine system for Docling.  This package provides a pluggable inferenc`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 65`** (2 nodes): `Permite invocar o scanner via `python -m scanner`.`, `__main__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 66`** (2 nodes): `Exporters — escrevem o resultado da extração em formatos finais.`, `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 67`** (2 nodes): `Pós-processamento de Markdown extraído pelo OCR.  Corrige problemas conhecidos d`, `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 68`** (1 nodes): `Caminho do SQLite, sempre dentro do data_dir.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 69`** (1 nodes): `Pasta raiz dos jobs (`<data_dir>/jobs/`).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 70`** (1 nodes): `SQLAlchemy URL — async driver aiosqlite.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 81`** (1 nodes): `Check if a LaTeX string needs wrapping in braces for sub/superscript.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 94`** (1 nodes): `r"""         Set num_threads from the "alternative" envvar OMP_NUM_THREADS.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 95`** (1 nodes): `Emit deprecation warning if old field name is used during initialization.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 128`** (1 nodes): `Payload do /api/health (espelha spec Section 7.1).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 129`** (1 nodes): `Detecta device atual (CUDA disponível? GPU name?).      Honra `settings.device`:`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 130`** (1 nodes): `Tamanho do arquivo SQLite em MB. 0 se não existe ainda.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 131`** (1 nodes): `Espaço livre no filesystem do data_dir, em GB.      Se o data_dir ainda não exis`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 132`** (1 nodes): `Retorna (queue_depth, workers_busy) do pool, ou (0, 0) se off.      Em testes ou`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 133`** (1 nodes): `Retorna estado do servidor.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 134`** (1 nodes): `device é cuda | cpu (não 'auto' — já resolvido em runtime).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 135`** (1 nodes): `Phase 1A não tem worker pool ainda — queue_depth = 0.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 136`** (1 nodes): `version é o __version__ do scanner_api.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 137`** (1 nodes): `disk_free_gb > 0 num filesystem real.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 138`** (1 nodes): `Antes de Alembic upgrade, scanner.db não existe — tamanho = 0.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 139`** (1 nodes): `Factory para criar a app — facilita testes (cria app por test client).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 140`** (1 nodes): `Retorna estado do servidor.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 141`** (1 nodes): `Cria um data dir temporário e seta env vars necessárias.      SCANNER_VAPID_* sã`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 142`** (1 nodes): `httpx AsyncClient apontado para a app em ASGI mode.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 143`** (1 nodes): `Aplica todas as correções e retorna o texto pós-processado.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 144`** (1 nodes): `Concatena MDs num único arquivo com ToC.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `InputDocument` connect `Community 0` to `Community 1`, `Community 2`, `Community 3`, `Community 4`, `Community 6`, `Community 38`, `Community 8`, `Community 9`, `Community 11`, `Community 13`, `Community 14`, `Community 17`?**
  _High betweenness centrality (0.148) - this node is a cross-community bridge._
- **Why does `InputFormat` connect `Community 0` to `Community 1`, `Community 2`, `Community 3`, `Community 4`, `Community 6`, `Community 8`, `Community 9`, `Community 10`, `Community 11`, `Community 13`, `Community 14`?**
  _High betweenness centrality (0.131) - this node is a cross-community bridge._
- **Why does `AcceleratorOptions` connect `Community 4` to `Community 1`, `Community 2`, `Community 3`, `Community 7`, `Community 8`, `Community 9`, `Community 10`, `Community 11`, `Community 12`, `Community 13`, `Community 15`?**
  _High betweenness centrality (0.082) - this node is a cross-community bridge._
- **Are the 590 inferred relationships involving `InputDocument` (e.g. with `FormatOption` and `CsvFormatOption`) actually correct?**
  _`InputDocument` has 590 INFERRED edges - model-reasoned connections that need verification._
- **Are the 560 inferred relationships involving `InputFormat` (e.g. with `FormatOption` and `CsvFormatOption`) actually correct?**
  _`InputFormat` has 560 INFERRED edges - model-reasoned connections that need verification._
- **Are the 393 inferred relationships involving `AcceleratorOptions` (e.g. with `BaseOptions` and `TableFormerMode`) actually correct?**
  _`AcceleratorOptions` has 393 INFERRED edges - model-reasoned connections that need verification._
- **Are the 373 inferred relationships involving `ConversionResult` (e.g. with `FormatOption` and `CsvFormatOption`) actually correct?**
  _`ConversionResult` has 373 INFERRED edges - model-reasoned connections that need verification._