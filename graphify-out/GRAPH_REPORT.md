# Graph Report - Scanner de imagens  (2026-05-02)

## Corpus Check
- 361 files · ~5,854,241 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 4343 nodes · 19448 edges · 48 communities detected
- Extraction: 30% EXTRACTED · 70% INFERRED · 0% AMBIGUOUS · INFERRED: 13661 edges (avg confidence: 0.54)
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
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 96|Community 96]]
- [[_COMMUNITY_Community 97|Community 97]]

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
- `DocumentConverter` --calls--> `test_converter_default_maps_image_to_image_backend()`  [INFERRED]
  docling-main\docling-main\docling\document_converter.py → docling-main\docling-main\tests\test_backend_image_native.py
- `DocumentConverter` --calls--> `converter()`  [INFERRED]
  docling-main\docling-main\docling\document_converter.py → docling-main\docling-main\tests\test_backend_vtt.py
- `DocumentConverter` --calls--> `test_convert_no_pipeline_wout_exception()`  [INFERRED]
  docling-main\docling-main\docling\document_converter.py → docling-main\docling-main\tests\test_invalid_input.py
- `DocumentConverter` --calls--> `test_convert_no_pipeline_with_exception()`  [INFERRED]
  docling-main\docling-main\docling\document_converter.py → docling-main\docling-main\tests\test_invalid_input.py
- `DocumentConverter` --calls--> `test_page_range()`  [INFERRED]
  docling-main\docling-main\docling\document_converter.py → docling-main\docling-main\tests\test_options.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.01
Nodes (534): DeclarativeDocumentBackend, PaginatedDocumentBackend, DeclarativeDocumentBackend.      A declarative document backend is a backend tha, DeclarativeDocumentBackend.      A declarative document backend is a backend tha, Extract the item marker (number or bullet symbol) and the text of the item., Parse an image macro, extracting its path and attributes.         Syntax: image:, Parses the ASCII into a structured document model., Main function that orchestrates the parsing by yielding components:         titl (+526 more)

### Community 1 - "Community 1"
Cohesion: 0.02
Nodes (287): AbstractDocumentBackend, PdfDocumentBackend, PdfPageBackend, BaseModelWithOptions, BasePageModel, BaseTableStructureModel, BaseVlmPageModel, show_external_plugins_callback() (+279 more)

### Community 2 - "Community 2"
Cohesion: 0.02
Nodes (321): BaseImageClassificationEngineOptions, BaseObjectDetectionEngineOptions, BaseVlmEngine, BaseVlmEngineOptions, HfVisionModelMixin, Shared HuggingFace helpers for vision inference engine families., Get the label mapping for this model., Shared utility mixin for HF vision model loading and label conversion. (+313 more)

### Community 3 - "Community 3"
Cohesion: 0.03
Nodes (303): BaseItemAndImageEnrichmentModel, BaseOcrModel, _BaseChartExtractionModelGraniteVision, ChartExtractionModelGraniteVision, ChartExtractionModelGraniteVisionV4, download_models(), Check if a value is numeric (int or float)., Transform a pandas DataFrame into a TableData object.          Automatically inf (+295 more)

### Community 4 - "Community 4"
Cohesion: 0.02
Nodes (231): AbstractDocumentBackend, __init__(), AsciiDocBackend, CsvDocumentBackend, DoclingParseDocumentBackend, DoclingParseV2DocumentBackend, DoclingParseV4DocumentBackend, HTMLDocumentBackend (+223 more)

### Community 5 - "Community 5"
Cohesion: 0.02
Nodes (222): PyPdfiumDocumentBackend, BaseExtractionPipeline, BaseFormatOption, BaseModel, BaseSettings, BaseVlmModel, ErrorItem, OutputFormat (+214 more)

### Community 6 - "Community 6"
Cohesion: 0.02
Nodes (139): AnnotatedText, AnnotatedTextList, _clean_unicode(), _collect_parent_format_tags(), convert(), _dom_distance_between_tags(), _extract_direct_text(), _extract_form_marker_text() (+131 more)

### Community 7 - "Community 7"
Cohesion: 0.02
Nodes (113): convert(), __init__(), is_valid(), Shared inference-engine utilities., KserveV2Client, Shared protocol for KServe v2 transport clients., Transport-agnostic KServe v2 client interface., Fetch model metadata for tensor name/schema resolution. (+105 more)

### Community 8 - "Community 8"
Cohesion: 0.02
Nodes (133): extract(), extract_all(), _get_pipeline_options_hash(), DoclingEngine, ExtractionResult, Adapter para Docling DocumentConverter.  Encapsula toda a interação com a API al, Extrai conteúdo do arquivo `source` para `markdown_target` + imagens em `artifac, Resultado da extração — payload puro, paths para arquivos já gravados.      O Do (+125 more)

### Community 9 - "Community 9"
Cohesion: 0.02
Nodes (24): ABC, DoclingParsePageBackend, # TODO: Take width and height from docling-parse., _ImagePageBackend, _close_native_document(), _close_native_page(), ManagedPdfiumDocumentBackend, ManagedPdfiumPageBackend (+16 more)

### Community 10 - "Community 10"
Cohesion: 0.05
Nodes (53): BaseLayoutModel, BaseLayoutOptions, Cluster, LayoutPrediction, LayoutObjectDetectionOptions, LayoutOptions, Internal options for the experimental TableCrops layout model., Options for TableCropsLayoutModel (internal-only). (+45 more)

### Community 11 - "Community 11"
Cohesion: 0.05
Nodes (47): BaseImageClassificationEngine, HfImageClassificationEngineBase, ApiKserveV2ImageClassificationEngine, KServe v2 remote implementation for image-classification models., Run inference on a batch of images against a KServe v2 endpoint., Remote image-classification engine backed by KServe v2-compatible serving., Initialize preprocessor/labels and prepare remote client., BaseImageClassificationEngine (+39 more)

### Community 12 - "Community 12"
Cohesion: 0.05
Nodes (22): convert(), _get_format_from_run(), _group_cell_elements(), __init__(), is_valid(), _isolated_list_context(), load_msword_file(), MsWordDocumentBackend (+14 more)

### Community 13 - "Community 13"
Cohesion: 0.06
Nodes (44): BaseObjectDetectionEngine, Helpers for KServe transport URL handling., Resolve runtime base URL for KServe transport clients.      HTTP accepts either, resolve_kserve_transport_base_url(), HfObjectDetectionEngineBase, HfVisionModelMixin, ApiKserveV2ObjectDetectionEngine, KServe v2 remote implementation for object-detection models. (+36 more)

### Community 14 - "Community 14"
Cohesion: 0.06
Nodes (57): get_converter(), get_md_paths(), test_convert_leading_dash_sequences(), test_convert_valid(), test_e2e_md_conversions(), converter(), _create_vtt_stream(), _process_vtt_doc() (+49 more)

### Community 15 - "Community 15"
Cohesion: 0.06
Nodes (33): BasePipeline, _label_value(), _meets_confidence(), _passes_classification(), PictureDescriptionBaseModel, PictureDescriptionApiModel, PictureDescriptionBaseModel, PictureDescriptionBaseOptions (+25 more)

### Community 16 - "Community 16"
Cohesion: 0.06
Nodes (44): _apply_accent(), fix_accents(), fix_spaces_and_punct(), fix_zero_as_o(), merge_into_book(), process_markdown(), Implementação do pós-processador PT-BR (lib).  Movido de `scripts/postprocess_md, Aplica todas as correções e retorna o texto pós-processado. (+36 more)

### Community 17 - "Community 17"
Cohesion: 0.12
Nodes (27): _detect_csv(), _detect_html_xhtml(), _detect_mets_gbs(), _detect_office_mime_from_zip(), _DocumentConversionInput, _guess_from_content(), _mime_from_extension(), _get_backend_from_stream() (+19 more)

### Community 18 - "Community 18"
Cohesion: 0.13
Nodes (22): auto_tags(), build_frontmatter(), ChatFile, collect_inputs(), detect_source(), extract_title(), inject_wikilinks(), list_permanent_titles() (+14 more)

### Community 19 - "Community 19"
Cohesion: 0.17
Nodes (16): _get_current_level(), _get_current_parent(), _is_caption(), _is_list_item(), _is_picture(), _is_section_header(), _is_table_line(), _is_title() (+8 more)

### Community 20 - "Community 20"
Cohesion: 0.2
Nodes (3): MacroHandlerMixin, _nodes_to_text(), _process_nodes()

### Community 21 - "Community 21"
Cohesion: 0.15
Nodes (7): _parse_orientation(), TesseractOcrCliModel, test_rotate_bounding_box(), map_tesseract_script(), parse_tesseract_orientation(), tesseract_box_to_bounding_rectangle(), rotate_bounding_box()

### Community 22 - "Community 22"
Cohesion: 0.2
Nodes (5): AdvancedPIIObfuscator, _build_gliner_model(), _build_simple_ner_pipeline(), main(), SimplePiiObfuscator

### Community 23 - "Community 23"
Cohesion: 0.28
Nodes (6): _clean_math(), EnvironmentHandlerMixin, _extract_macro_arg(), _extract_verbatim_content(), _parse_table(), _process_nodes()

### Community 25 - "Community 25"
Cohesion: 0.23
Nodes (7): _expand_custom_macro_invocation(), _expand_macros(), _extract_macro_arg(), _parse_latex_fragment_to_text(), _process_nodes(), Return ``(text, consumed_following)`` for a single macro node., TextHelperMixin

### Community 26 - "Community 26"
Cohesion: 0.36
Nodes (7): _add_child_elements(), _flatten_table_grid(), Find item in document from a reference path, # TODO: Infer if this is a numbered or a bullet list item, # TODO: Infer if this is a numbered or a bullet list item, resolve_item(), to_docling_document()

### Community 27 - "Community 27"
Cohesion: 0.62
Nodes (6): _client(), create_conversion_options(), main(), run_json_task_flow_with_watch(), run_markdown_task_flow_without_watch(), _service_url()

### Community 28 - "Community 28"
Cohesion: 0.7
Nodes (2): _expand_macros(), MathHandlerMixin

### Community 29 - "Community 29"
Cohesion: 0.5
Nodes (1): TableHelperMixin

### Community 31 - "Community 31"
Cohesion: 0.5
Nodes (1): Common KServe v2 API configuration options mixin.

### Community 32 - "Community 32"
Cohesion: 0.67
Nodes (2): _get_backend(), test_asciidocs_examples()

### Community 33 - "Community 33"
Cohesion: 0.83
Nodes (3): _install_backend_import_stubs(), _load_msexcel_backend(), test_find_data_tables_handles_a_filled_last_excel_row()

### Community 34 - "Community 34"
Cohesion: 0.5
Nodes (3): Persistência do markdown extraído., Escreve o markdown em `target`, criando pastas pai se necessário.      Returns:, write_markdown()

### Community 36 - "Community 36"
Cohesion: 1.0
Nodes (1): Adapted from https://github.com/xiilei/dwml/blob/master/dwml/latex_dict.py On 23

### Community 37 - "Community 37"
Cohesion: 1.0
Nodes (1): ParseContext

### Community 38 - "Community 38"
Cohesion: 1.0
Nodes (1): Experimental modules for Docling.  This package contains experimental features t

### Community 39 - "Community 39"
Cohesion: 1.0
Nodes (1): Experimental datamodel modules.

### Community 40 - "Community 40"
Cohesion: 1.0
Nodes (1): Experimental models for Docling.

### Community 41 - "Community 41"
Cohesion: 1.0
Nodes (1): Experimental pipeline modules.

### Community 42 - "Community 42"
Cohesion: 1.0
Nodes (1): Inference engine system for Docling.  This package provides a pluggable inferenc

### Community 43 - "Community 43"
Cohesion: 1.0
Nodes (1): Permite invocar o scanner via `python -m scanner`.

### Community 44 - "Community 44"
Cohesion: 1.0
Nodes (1): Exporters — escrevem o resultado da extração em formatos finais.

### Community 45 - "Community 45"
Cohesion: 1.0
Nodes (1): Pós-processamento de Markdown extraído pelo OCR.  Corrige problemas conhecidos d

### Community 49 - "Community 49"
Cohesion: 1.0
Nodes (1): Check if a LaTeX string needs wrapping in braces for sub/superscript.

### Community 62 - "Community 62"
Cohesion: 1.0
Nodes (1): r"""         Set num_threads from the "alternative" envvar OMP_NUM_THREADS.

### Community 63 - "Community 63"
Cohesion: 1.0
Nodes (1): Emit deprecation warning if old field name is used during initialization.

### Community 96 - "Community 96"
Cohesion: 1.0
Nodes (1): Aplica todas as correções e retorna o texto pós-processado.

### Community 97 - "Community 97"
Cohesion: 1.0
Nodes (1): Concatena MDs num único arquivo com ToC.

## Knowledge Gaps
- **156 isolated node(s):** `Return the libreoffice cmd and optionally test it.`, `Detects the best available DOCX to PDF tool and returns a conversion function.`, `Adapted from https://github.com/xiilei/dwml/blob/master/dwml/latex_dict.py On 23`, `Office Math Markup Language (OMML)  Adapted from https://github.com/xiilei/dwml/`, `process children of the elm,return iterable` (+151 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 28`** (5 nodes): `math.py`, `_expand_macros()`, `MathHandlerMixin`, `._clean_math()`, `._process_math_node()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 29`** (5 nodes): `table.py`, `_nodes_to_text()`, `TableHelperMixin`, `._parse_table()`, `._process_table_macro_node()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (4 nodes): `grpc_use_binary_data()`, `Common KServe v2 API configuration options mixin.`, `_warn_deprecated_alias()`, `kserve_v2_options.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (4 nodes): `test_backend_asciidoc.py`, `_get_backend()`, `test_asciidocs_examples()`, `test_parse_picture()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (2 nodes): `latex_dict.py`, `Adapted from https://github.com/xiilei/dwml/blob/master/dwml/latex_dict.py On 23`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 37`** (2 nodes): `context.py`, `ParseContext`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (2 nodes): `__init__.py`, `Experimental modules for Docling.  This package contains experimental features t`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (2 nodes): `Experimental datamodel modules.`, `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 40`** (2 nodes): `__init__.py`, `Experimental models for Docling.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 41`** (2 nodes): `__init__.py`, `Experimental pipeline modules.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 42`** (2 nodes): `__init__.py`, `Inference engine system for Docling.  This package provides a pluggable inferenc`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 43`** (2 nodes): `Permite invocar o scanner via `python -m scanner`.`, `__main__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 44`** (2 nodes): `Exporters — escrevem o resultado da extração em formatos finais.`, `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 45`** (2 nodes): `Pós-processamento de Markdown extraído pelo OCR.  Corrige problemas conhecidos d`, `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (1 nodes): `Check if a LaTeX string needs wrapping in braces for sub/superscript.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 62`** (1 nodes): `r"""         Set num_threads from the "alternative" envvar OMP_NUM_THREADS.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 63`** (1 nodes): `Emit deprecation warning if old field name is used during initialization.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 96`** (1 nodes): `Aplica todas as correções e retorna o texto pós-processado.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 97`** (1 nodes): `Concatena MDs num único arquivo com ToC.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `InputDocument` connect `Community 0` to `Community 32`, `Community 1`, `Community 3`, `Community 4`, `Community 5`, `Community 6`, `Community 7`, `Community 9`, `Community 12`, `Community 14`, `Community 17`?**
  _High betweenness centrality (0.146) - this node is a cross-community bridge._
- **Why does `InputFormat` connect `Community 0` to `Community 1`, `Community 2`, `Community 3`, `Community 4`, `Community 5`, `Community 6`, `Community 8`, `Community 9`, `Community 12`, `Community 14`, `Community 17`, `Community 22`?**
  _High betweenness centrality (0.139) - this node is a cross-community bridge._
- **Why does `AcceleratorOptions` connect `Community 3` to `Community 1`, `Community 2`, `Community 4`, `Community 5`, `Community 7`, `Community 8`, `Community 10`, `Community 11`, `Community 12`, `Community 13`, `Community 15`, `Community 21`?**
  _High betweenness centrality (0.104) - this node is a cross-community bridge._
- **Are the 590 inferred relationships involving `InputDocument` (e.g. with `FormatOption` and `CsvFormatOption`) actually correct?**
  _`InputDocument` has 590 INFERRED edges - model-reasoned connections that need verification._
- **Are the 560 inferred relationships involving `InputFormat` (e.g. with `FormatOption` and `CsvFormatOption`) actually correct?**
  _`InputFormat` has 560 INFERRED edges - model-reasoned connections that need verification._
- **Are the 393 inferred relationships involving `AcceleratorOptions` (e.g. with `BaseOptions` and `TableFormerMode`) actually correct?**
  _`AcceleratorOptions` has 393 INFERRED edges - model-reasoned connections that need verification._
- **Are the 373 inferred relationships involving `ConversionResult` (e.g. with `FormatOption` and `CsvFormatOption`) actually correct?**
  _`ConversionResult` has 373 INFERRED edges - model-reasoned connections that need verification._