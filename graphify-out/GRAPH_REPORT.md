# Graph Report - Scanner de imagens  (2026-05-02)

## Corpus Check
- 356 files · ~5,848,030 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 4235 nodes · 19215 edges · 48 communities detected
- Extraction: 30% EXTRACTED · 70% INFERRED · 0% AMBIGUOUS · INFERRED: 13517 edges (avg confidence: 0.53)
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
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 65|Community 65]]

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
- `test_converter_default_maps_image_to_image_backend()` --calls--> `DocumentConverter`  [INFERRED]
  docling-main\docling-main\tests\test_backend_image_native.py → docling-main\docling-main\docling\document_converter.py
- `converter()` --calls--> `DocumentConverter`  [INFERRED]
  docling-main\docling-main\tests\test_backend_vtt.py → docling-main\docling-main\docling\document_converter.py
- `test_convert_no_pipeline_wout_exception()` --calls--> `DocumentConverter`  [INFERRED]
  docling-main\docling-main\tests\test_invalid_input.py → docling-main\docling-main\docling\document_converter.py
- `test_convert_no_pipeline_with_exception()` --calls--> `DocumentConverter`  [INFERRED]
  docling-main\docling-main\tests\test_invalid_input.py → docling-main\docling-main\docling\document_converter.py
- `test_page_range()` --calls--> `DocumentConverter`  [INFERRED]
  docling-main\docling-main\tests\test_options.py → docling-main\docling-main\docling\document_converter.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.01
Nodes (543): DeclarativeDocumentBackend, PaginatedDocumentBackend, DeclarativeDocumentBackend.      A declarative document backend is a backend tha, DeclarativeDocumentBackend.      A declarative document backend is a backend tha, Extract the item marker (number or bullet symbol) and the text of the item., Parse an image macro, extracting its path and attributes.         Syntax: image:, Parses the ASCII into a structured document model., Main function that orchestrates the parsing by yielding components:         titl (+535 more)

### Community 1 - "Community 1"
Cohesion: 0.02
Nodes (301): AbstractDocumentBackend, PdfDocumentBackend, PdfPageBackend, BaseModelWithOptions, BasePageModel, BaseTableStructureModel, BaseVlmPageModel, show_external_plugins_callback() (+293 more)

### Community 2 - "Community 2"
Cohesion: 0.03
Nodes (308): BaseImageClassificationEngineOptions, BaseObjectDetectionEngineOptions, BaseVlmEngine, BaseVlmEngineOptions, HfVisionModelMixin, Shared HuggingFace helpers for vision inference engine families., Get the label mapping for this model., Shared utility mixin for HF vision model loading and label conversion. (+300 more)

### Community 3 - "Community 3"
Cohesion: 0.03
Nodes (306): BaseItemAndImageEnrichmentModel, BaseOcrModel, _BaseChartExtractionModelGraniteVision, ChartExtractionModelGraniteVision, ChartExtractionModelGraniteVisionV4, download_models(), Check if a value is numeric (int or float)., Transform a pandas DataFrame into a TableData object.          Automatically inf (+298 more)

### Community 4 - "Community 4"
Cohesion: 0.02
Nodes (223): PyPdfiumDocumentBackend, BaseExtractionPipeline, BaseFormatOption, BaseModel, BaseSettings, BaseVlmModel, ErrorItem, OutputFormat (+215 more)

### Community 5 - "Community 5"
Cohesion: 0.02
Nodes (214): AbstractDocumentBackend, __init__(), AsciiDocBackend, CsvDocumentBackend, DoclingParseDocumentBackend, DoclingParseV2DocumentBackend, DoclingParseV4DocumentBackend, ImageDocumentBackend (+206 more)

### Community 6 - "Community 6"
Cohesion: 0.02
Nodes (126): __init__(), convert(), __init__(), is_valid(), BaseImageClassificationEngine, Shared inference-engine utilities., KserveV2Client, Shared protocol for KServe v2 transport clients. (+118 more)

### Community 7 - "Community 7"
Cohesion: 0.02
Nodes (121): AnnotatedText, AnnotatedTextList, _clean_unicode(), _collect_parent_format_tags(), convert(), _dom_distance_between_tags(), _extract_direct_text(), _extract_form_marker_text() (+113 more)

### Community 8 - "Community 8"
Cohesion: 0.02
Nodes (29): ABC, DoclingParsePageBackend, # TODO: Take width and height from docling-parse., _ImagePageBackend, _close_native_document(), _close_native_page(), ManagedPdfiumDocumentBackend, ManagedPdfiumPageBackend (+21 more)

### Community 9 - "Community 9"
Cohesion: 0.04
Nodes (57): BaseObjectDetectionEngine, _AvailableModels, download(), download_hf_repo(), Helpers for KServe transport URL handling., Resolve runtime base URL for KServe transport clients.      HTTP accepts either, resolve_kserve_transport_base_url(), HfObjectDetectionEngineBase (+49 more)

### Community 10 - "Community 10"
Cohesion: 0.04
Nodes (70): DoclingEngine, Engines de extração. Atualmente: Docling (default)., Exception, _ensure_pandoc(), Conversão Markdown → DOCX usando pandoc.  Decisão registrada em `vault/projeto/d, Converte um arquivo Markdown para DOCX preservando imagens e estrutura.      Arg, Garante que pandoc está disponível.      Ordem de busca:     1. PATH do shell (`, write_docx() (+62 more)

### Community 11 - "Community 11"
Cohesion: 0.04
Nodes (47): BaseLayoutModel, BaseLayoutOptions, Cluster, LayoutPrediction, Internal options for the experimental TableCrops layout model., Options for TableCropsLayoutModel (internal-only)., TableCropsLayoutOptions, main() (+39 more)

### Community 12 - "Community 12"
Cohesion: 0.05
Nodes (22): convert(), _get_format_from_run(), _group_cell_elements(), __init__(), is_valid(), _isolated_list_context(), load_msword_file(), MsWordDocumentBackend (+14 more)

### Community 13 - "Community 13"
Cohesion: 0.04
Nodes (43): BasePipeline, _label_value(), _meets_confidence(), _passes_classification(), PictureDescriptionBaseModel, PictureDescriptionApiModel, PictureDescriptionVlmModel, PictureDescriptionBaseModel (+35 more)

### Community 14 - "Community 14"
Cohesion: 0.06
Nodes (57): get_converter(), get_md_paths(), test_convert_leading_dash_sequences(), test_convert_valid(), test_e2e_md_conversions(), converter(), _create_vtt_stream(), _process_vtt_doc() (+49 more)

### Community 15 - "Community 15"
Cohesion: 0.12
Nodes (27): _detect_csv(), _detect_html_xhtml(), _detect_mets_gbs(), _detect_office_mime_from_zip(), _DocumentConversionInput, _guess_from_content(), _mime_from_extension(), _get_backend_from_stream() (+19 more)

### Community 16 - "Community 16"
Cohesion: 0.09
Nodes (14): BaseError, ConversionError, SecurityError, main(), download_models(), download_models(), _resolve_rapidocr_language(), generate_multimodal_pages() (+6 more)

### Community 17 - "Community 17"
Cohesion: 0.13
Nodes (22): auto_tags(), build_frontmatter(), ChatFile, collect_inputs(), detect_source(), extract_title(), inject_wikilinks(), list_permanent_titles() (+14 more)

### Community 18 - "Community 18"
Cohesion: 0.17
Nodes (16): _get_current_level(), _get_current_parent(), _is_caption(), _is_list_item(), _is_picture(), _is_section_header(), _is_table_line(), _is_title() (+8 more)

### Community 19 - "Community 19"
Cohesion: 0.2
Nodes (3): MacroHandlerMixin, _nodes_to_text(), _process_nodes()

### Community 20 - "Community 20"
Cohesion: 0.15
Nodes (7): _parse_orientation(), TesseractOcrCliModel, test_rotate_bounding_box(), map_tesseract_script(), parse_tesseract_orientation(), tesseract_box_to_bounding_rectangle(), rotate_bounding_box()

### Community 21 - "Community 21"
Cohesion: 0.18
Nodes (6): AdvancedPIIObfuscator, _build_gliner_model(), _build_simple_ner_pipeline(), main(), SimplePiiObfuscator, pipeline()

### Community 22 - "Community 22"
Cohesion: 0.21
Nodes (13): mock_response_factory(), Tests for api_image_request module., Test cases for api_image_request function., test_content_filter_finish_reason(), test_length_finish_reason(), test_stop_finish_reason(), test_tool_calls_response(), TestApiImageRequest (+5 more)

### Community 23 - "Community 23"
Cohesion: 0.28
Nodes (6): _clean_math(), EnvironmentHandlerMixin, _extract_macro_arg(), _extract_verbatim_content(), _parse_table(), _process_nodes()

### Community 25 - "Community 25"
Cohesion: 0.23
Nodes (7): _expand_custom_macro_invocation(), _expand_macros(), _extract_macro_arg(), _parse_latex_fragment_to_text(), _process_nodes(), Return ``(text, consumed_following)`` for a single macro node., TextHelperMixin

### Community 26 - "Community 26"
Cohesion: 0.27
Nodes (9): _collect_annotation_content(), parse_deepseekocr_markdown(), _parse_table_html(), _process_annotation_item(), Utilities for parsing DeepSeek OCR annotated markdown format., Collect content for an annotation.      Args:         lines: All lines from the, Process and add a single annotation item to the document.      Args:         lab, Parse DeepSeek OCR markdown with label[[x1, y1, x2, y2]] format.      This funct (+1 more)

### Community 27 - "Community 27"
Cohesion: 0.33
Nodes (9): _apply_accent(), fix_accents(), fix_spaces_and_punct(), fix_zero_as_o(), main(), merge_into_book(), process_markdown(), Aplica todas as correções e retorna o texto pós-processado. (+1 more)

### Community 28 - "Community 28"
Cohesion: 0.36
Nodes (7): _add_child_elements(), _flatten_table_grid(), Find item in document from a reference path, # TODO: Infer if this is a numbered or a bullet list item, # TODO: Infer if this is a numbered or a bullet list item, resolve_item(), to_docling_document()

### Community 29 - "Community 29"
Cohesion: 0.62
Nodes (6): _client(), create_conversion_options(), main(), run_json_task_flow_with_watch(), run_markdown_task_flow_without_watch(), _service_url()

### Community 30 - "Community 30"
Cohesion: 0.48
Nodes (5): _get_backend(), test_crop_page_image(), test_get_text_from_rect(), test_num_pages(), test_text_cell_counts()

### Community 31 - "Community 31"
Cohesion: 0.7
Nodes (2): _expand_macros(), MathHandlerMixin

### Community 32 - "Community 32"
Cohesion: 0.5
Nodes (1): TableHelperMixin

### Community 34 - "Community 34"
Cohesion: 0.5
Nodes (1): Common KServe v2 API configuration options mixin.

### Community 35 - "Community 35"
Cohesion: 0.67
Nodes (2): _get_backend(), test_asciidocs_examples()

### Community 36 - "Community 36"
Cohesion: 0.83
Nodes (3): _install_backend_import_stubs(), _load_msexcel_backend(), test_find_data_tables_handles_a_filled_last_excel_row()

### Community 37 - "Community 37"
Cohesion: 0.5
Nodes (3): Persistência do markdown extraído., Escreve o markdown em `target`, criando pastas pai se necessário.      Returns:, write_markdown()

### Community 39 - "Community 39"
Cohesion: 1.0
Nodes (1): Adapted from https://github.com/xiilei/dwml/blob/master/dwml/latex_dict.py On 23

### Community 40 - "Community 40"
Cohesion: 1.0
Nodes (1): ParseContext

### Community 41 - "Community 41"
Cohesion: 1.0
Nodes (1): Experimental modules for Docling.  This package contains experimental features t

### Community 42 - "Community 42"
Cohesion: 1.0
Nodes (1): Experimental datamodel modules.

### Community 43 - "Community 43"
Cohesion: 1.0
Nodes (1): Experimental models for Docling.

### Community 44 - "Community 44"
Cohesion: 1.0
Nodes (1): Experimental pipeline modules.

### Community 45 - "Community 45"
Cohesion: 1.0
Nodes (1): Inference engine system for Docling.  This package provides a pluggable inferenc

### Community 46 - "Community 46"
Cohesion: 1.0
Nodes (1): Permite invocar o scanner via `python -m scanner`.

### Community 47 - "Community 47"
Cohesion: 1.0
Nodes (1): Exporters — escrevem o resultado da extração em formatos finais.

### Community 51 - "Community 51"
Cohesion: 1.0
Nodes (1): Check if a LaTeX string needs wrapping in braces for sub/superscript.

### Community 64 - "Community 64"
Cohesion: 1.0
Nodes (1): r"""         Set num_threads from the "alternative" envvar OMP_NUM_THREADS.

### Community 65 - "Community 65"
Cohesion: 1.0
Nodes (1): Emit deprecation warning if old field name is used during initialization.

## Knowledge Gaps
- **134 isolated node(s):** `Return the libreoffice cmd and optionally test it.`, `Detects the best available DOCX to PDF tool and returns a conversion function.`, `Adapted from https://github.com/xiilei/dwml/blob/master/dwml/latex_dict.py On 23`, `Office Math Markup Language (OMML)  Adapted from https://github.com/xiilei/dwml/`, `process children of the elm,return iterable` (+129 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 31`** (5 nodes): `math.py`, `_expand_macros()`, `MathHandlerMixin`, `._clean_math()`, `._process_math_node()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (5 nodes): `table.py`, `_nodes_to_text()`, `TableHelperMixin`, `._parse_table()`, `._process_table_macro_node()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (4 nodes): `grpc_use_binary_data()`, `Common KServe v2 API configuration options mixin.`, `_warn_deprecated_alias()`, `kserve_v2_options.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (4 nodes): `test_backend_asciidoc.py`, `_get_backend()`, `test_asciidocs_examples()`, `test_parse_picture()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (2 nodes): `latex_dict.py`, `Adapted from https://github.com/xiilei/dwml/blob/master/dwml/latex_dict.py On 23`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 40`** (2 nodes): `context.py`, `ParseContext`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 41`** (2 nodes): `__init__.py`, `Experimental modules for Docling.  This package contains experimental features t`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 42`** (2 nodes): `Experimental datamodel modules.`, `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 43`** (2 nodes): `__init__.py`, `Experimental models for Docling.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 44`** (2 nodes): `__init__.py`, `Experimental pipeline modules.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 45`** (2 nodes): `__init__.py`, `Inference engine system for Docling.  This package provides a pluggable inferenc`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (2 nodes): `Permite invocar o scanner via `python -m scanner`.`, `__main__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (2 nodes): `Exporters — escrevem o resultado da extração em formatos finais.`, `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 51`** (1 nodes): `Check if a LaTeX string needs wrapping in braces for sub/superscript.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 64`** (1 nodes): `r"""         Set num_threads from the "alternative" envvar OMP_NUM_THREADS.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 65`** (1 nodes): `Emit deprecation warning if old field name is used during initialization.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `InputDocument` connect `Community 0` to `Community 1`, `Community 3`, `Community 4`, `Community 5`, `Community 35`, `Community 7`, `Community 8`, `Community 12`, `Community 14`, `Community 15`, `Community 30`?**
  _High betweenness centrality (0.150) - this node is a cross-community bridge._
- **Why does `InputFormat` connect `Community 0` to `Community 1`, `Community 2`, `Community 3`, `Community 4`, `Community 5`, `Community 7`, `Community 8`, `Community 10`, `Community 12`, `Community 14`, `Community 15`, `Community 21`?**
  _High betweenness centrality (0.141) - this node is a cross-community bridge._
- **Why does `AcceleratorOptions` connect `Community 3` to `Community 1`, `Community 2`, `Community 4`, `Community 5`, `Community 6`, `Community 9`, `Community 10`, `Community 11`, `Community 12`, `Community 13`, `Community 20`?**
  _High betweenness centrality (0.104) - this node is a cross-community bridge._
- **Are the 590 inferred relationships involving `InputDocument` (e.g. with `FormatOption` and `CsvFormatOption`) actually correct?**
  _`InputDocument` has 590 INFERRED edges - model-reasoned connections that need verification._
- **Are the 560 inferred relationships involving `InputFormat` (e.g. with `FormatOption` and `CsvFormatOption`) actually correct?**
  _`InputFormat` has 560 INFERRED edges - model-reasoned connections that need verification._
- **Are the 393 inferred relationships involving `AcceleratorOptions` (e.g. with `BaseOptions` and `TableFormerMode`) actually correct?**
  _`AcceleratorOptions` has 393 INFERRED edges - model-reasoned connections that need verification._
- **Are the 373 inferred relationships involving `ConversionResult` (e.g. with `FormatOption` and `CsvFormatOption`) actually correct?**
  _`ConversionResult` has 373 INFERRED edges - model-reasoned connections that need verification._