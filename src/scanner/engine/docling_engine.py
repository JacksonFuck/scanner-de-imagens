"""Adapter para Docling DocumentConverter.

Encapsula toda a interação com a API alta do Docling (`DocumentConverter`).
A escolha por API alta (vs. mexer com backends low-level) está registrada em
`vault/projeto/decisoes.md#motor-extracao`.

Decisões aplicadas:
- OCR engine: EasyOCR (default do Docling, bom para PT)
- Image mode: REFERENCED — imagens viram arquivos sibling do .md, não inline base64
- Aceita JPG/PNG/PDF nativamente — Docling roteia internamente para o backend correto
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from scanner.errors import ConfigurationError, ConversionError, InvalidInputError

if TYPE_CHECKING:
    from docling.datamodel.document import ConversionResult

log = logging.getLogger(__name__)

# Formatos aceitos pelo Docling que vamos suportar nesta release
SUPPORTED_EXTENSIONS: frozenset[str] = frozenset(
    {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".webp", ".pdf"}
)


@dataclass(slots=True, frozen=True)
class ExtractionResult:
    """Resultado da extração — payload puro, paths para arquivos já gravados.

    O Docling 2.92+ usa `save_as_markdown` que escreve `.md` + extrai imagens
    atomicamente para `artifacts_dir`. Por isso retornamos `markdown_path` (já
    no destino final) em vez da string em memória.
    """

    source: Path
    markdown_path: Path  # arquivo .md já gravado pelo Docling
    images: tuple[Path, ...]  # arquivos de imagem extraídos (paths absolutos)
    page_count: int


class DoclingEngine:
    """Wrapper fino do `DocumentConverter` do Docling.

    Inicialização cara (carrega modelos). Reuse a mesma instância para batches.

    Auto-detecção de GPU: se `device='auto'` (default) e PyTorch+CUDA estão
    disponíveis, usa GPU. Caso contrário cai para CPU silenciosamente.
    """

    def __init__(
        self,
        *,
        do_ocr: bool = True,
        do_table_structure: bool = True,
        device: str = "auto",  # 'auto' | 'cuda' | 'cpu'
        ocr_languages: list[str] | None = None,
        images_scale: float = 3.0,
        force_full_page_ocr: bool = True,
    ) -> None:
        # Import tardio: a importação do docling demora ~2s e baixa modelos no primeiro
        # uso. Não queremos pagar esse custo em testes que não tocam o engine.
        try:
            from docling.datamodel.accelerator_options import (
                AcceleratorDevice,
                AcceleratorOptions,
            )
            from docling.datamodel.base_models import InputFormat
            from docling.datamodel.pipeline_options import (
                EasyOcrOptions,
                PdfPipelineOptions,
            )
            from docling.document_converter import DocumentConverter, PdfFormatOption
        except ImportError as exc:
            raise ConfigurationError(
                "Docling não está instalado. Rode: pip install docling"
            ) from exc

        resolved_device = self._resolve_device(device)
        accelerator = AcceleratorOptions(
            device=AcceleratorDevice.CUDA if resolved_device == "cuda" else AcceleratorDevice.CPU,
            num_threads=4,
        )

        # Por que PT precisa ser explícito: EasyOcrOptions default é
        # ['fr','de','es','en'] — sem PT acentos viram ASCII (ção -> cao).
        # 'pt' + 'en' cobre documentos brasileiros bilíngues e siglas em inglês.
        if ocr_languages is None:
            ocr_languages = ["pt", "en"]
        ocr_options = EasyOcrOptions(
            lang=ocr_languages,
            force_full_page_ocr=force_full_page_ocr,
            confidence_threshold=0.3,  # mais permissivo: aceita caracteres acentuados
            use_gpu=(resolved_device == "cuda"),
        )

        pipeline_options = PdfPipelineOptions()
        pipeline_options.accelerator_options = accelerator
        pipeline_options.do_ocr = do_ocr
        pipeline_options.do_table_structure = do_table_structure
        pipeline_options.ocr_options = ocr_options
        # Gera imagens das páginas e elementos visuais em alta resolução
        pipeline_options.generate_page_images = True
        pipeline_options.generate_picture_images = True
        pipeline_options.images_scale = images_scale  # 3x = melhor OCR em fotos

        self._converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
                InputFormat.IMAGE: PdfFormatOption(pipeline_options=pipeline_options),
            }
        )
        log.info(
            "DocumentConverter inicializado (do_ocr=%s, device=%s, langs=%s, scale=%.1fx)",
            do_ocr, resolved_device, ocr_languages, images_scale,
        )

    @staticmethod
    def _resolve_device(requested: str) -> str:
        """Resolve 'auto' para 'cuda' se disponível, senão 'cpu'."""
        if requested == "cpu":
            return "cpu"
        if requested == "cuda":
            # Validação explícita: avisa se cuda foi pedido mas não disponível
            try:
                import torch
                if not torch.cuda.is_available():
                    log.warning("CUDA pedido mas não disponível — caindo para CPU")
                    return "cpu"
            except ImportError:
                log.warning("PyTorch não instalado — usando CPU")
                return "cpu"
            return "cuda"
        # auto
        try:
            import torch
            return "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            return "cpu"

    def extract(
        self,
        source: Path,
        *,
        markdown_target: Path,
        artifacts_dir: Path,
    ) -> ExtractionResult:
        """Extrai conteúdo do arquivo `source` para `markdown_target` + imagens em `artifacts_dir`.

        Args:
            source: Caminho para JPG/PNG/PDF/etc.
            markdown_target: Caminho final do `.md` (será criado/sobrescrito).
            artifacts_dir: Pasta onde imagens referenciadas serão escritas.

        Returns:
            ExtractionResult com paths absolutos dos arquivos gravados.

        Raises:
            InvalidInputError: arquivo não existe ou extensão não suportada.
            ConversionError: Docling falhou durante a conversão.
        """
        self._validate_source(source)
        markdown_target.parent.mkdir(parents=True, exist_ok=True)
        artifacts_dir.mkdir(parents=True, exist_ok=True)

        from docling_core.types.doc import ImageRefMode  # type: ignore[import-not-found]

        log.info("Extraindo: %s", source.name)
        try:
            result: ConversionResult = self._converter.convert(str(source))
        except Exception as exc:  # Docling lança vários tipos diferentes
            raise ConversionError(f"Docling falhou em {source.name}: {exc}") from exc

        try:
            result.document.save_as_markdown(
                filename=markdown_target,
                artifacts_dir=artifacts_dir,
                image_mode=ImageRefMode.REFERENCED,
            )
        except Exception as exc:
            raise ConversionError(f"Falha ao gravar markdown de {source.name}: {exc}") from exc

        images = tuple(
            sorted(artifacts_dir.glob("*.png"))
            + sorted(artifacts_dir.glob("*.jpg"))
            + sorted(artifacts_dir.glob("*.jpeg"))
        )
        page_count = len(getattr(result.document, "pages", {})) or 1
        log.info(
            "Extração concluída: %d página(s), %d imagem(ns), markdown=%s",
            page_count, len(images), markdown_target.name,
        )

        return ExtractionResult(
            source=source.resolve(),
            markdown_path=markdown_target.resolve(),
            images=images,
            page_count=page_count,
        )

    @staticmethod
    def _validate_source(source: Path) -> None:
        if not source.exists():
            raise InvalidInputError(f"Arquivo não encontrado: {source}")
        if not source.is_file():
            raise InvalidInputError(f"Não é arquivo: {source}")
        ext = source.suffix.lower()
        if ext not in SUPPORTED_EXTENSIONS:
            raise InvalidInputError(
                f"Formato não suportado: {ext}. "
                f"Aceitos: {sorted(SUPPORTED_EXTENSIONS)}"
            )
