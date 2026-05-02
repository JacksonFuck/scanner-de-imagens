"""Orquestrador — costura ingest → engine → exports.

Função pública `scan()` é o ponto de entrada usado pela CLI e por testes.
Toda a complexidade fica aqui; a CLI é só apresentação.
"""

from __future__ import annotations

import logging
import warnings
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

from scanner.engine.docling_engine import SUPPORTED_EXTENSIONS, DoclingEngine
from scanner.errors import InvalidInputError
from scanner.export import write_docx, write_pdf

log = logging.getLogger(__name__)


class OutputFormat(StrEnum):
    """Formatos de saída solicitáveis.

    BOTH é DEPRECATED desde v0.2 — use ALL. Permanece como alias por
    retrocompatibilidade até v0.3, quando será removido. Use `formats_for()`
    para resolver o enum num conjunto de formatos concretos (que emite
    DeprecationWarning ao receber BOTH).
    """

    MD = "md"
    DOCX = "docx"
    PDF = "pdf"
    ALL = "all"
    BOTH = "both"  # deprecated alias para ALL


# Mapeia cada valor do enum para o conjunto de formatos concretos a gerar.
# MD sempre é gerado (é o intermediário do Docling); os demais são opt-in.
_FORMATS_BY_ENUM: dict[OutputFormat, frozenset[str]] = {
    OutputFormat.MD: frozenset({"md"}),
    OutputFormat.DOCX: frozenset({"md", "docx"}),
    OutputFormat.PDF: frozenset({"md", "pdf"}),
    OutputFormat.ALL: frozenset({"md", "docx", "pdf"}),
    OutputFormat.BOTH: frozenset({"md", "docx", "pdf"}),  # = ALL
}


def formats_for(fmt: OutputFormat) -> frozenset[str]:
    """Resolve o enum para o conjunto de formatos concretos a gerar.

    Emite DeprecationWarning para `OutputFormat.BOTH` (alias temporário de
    `ALL`). O alias mantém comportamento idêntico até v0.3.

    Args:
        fmt: valor do enum OutputFormat.

    Returns:
        Frozenset de strings: subset de {'md', 'docx', 'pdf'}. 'md' sempre presente.
    """
    if fmt == OutputFormat.BOTH:
        warnings.warn(
            "OutputFormat.BOTH é deprecated. Use OutputFormat.ALL "
            "(produz MD + DOCX + PDF). Será removido em v0.3.",
            DeprecationWarning,
            stacklevel=2,
        )
    return _FORMATS_BY_ENUM[fmt]


@dataclass(slots=True)
class ScanRequest:
    """Pedido de scan — input + onde gravar + o que produzir."""

    source: Path
    output_dir: Path
    formats: OutputFormat = OutputFormat.MD
    do_ocr: bool = True
    do_table_structure: bool = True
    device: str = "auto"  # 'auto' | 'cuda' | 'cpu'
    ocr_languages: tuple[str, ...] = ("pt", "en")
    ocr_engine: str = "easyocr"  # 'easyocr' | 'tesseract'
    tessdata_path: str | None = None


@dataclass(slots=True)
class ScanResult:
    """Resultado: caminhos dos arquivos gerados."""

    source: Path
    markdown_path: Path
    docx_path: Path | None
    pdf_path: Path | None
    images: tuple[Path, ...]
    page_count: int
    artifacts_dir: Path

    def __str__(self) -> str:
        parts = [f"  - {self.markdown_path}"]
        if self.docx_path:
            parts.append(f"  - {self.docx_path}")
        if self.pdf_path:
            parts.append(f"  - {self.pdf_path}")
        if self.images:
            parts.append(f"  - {len(self.images)} imagem(ns) em {self.artifacts_dir}")
        return f"Scan de {self.source.name} ({self.page_count}p):\n" + "\n".join(parts)


@dataclass(slots=True)
class BatchResult:
    """Resultado de um batch (1+ arquivos)."""

    successes: list[ScanResult] = field(default_factory=list)
    failures: list[tuple[Path, Exception]] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.successes) + len(self.failures)


def scan(request: ScanRequest, *, engine: DoclingEngine | None = None) -> ScanResult:
    """Roda o pipeline para UM arquivo.

    Reuse `engine` quando processar múltiplos arquivos (init é caro).
    """
    _validate_request(request)
    engine = engine or DoclingEngine(
        do_ocr=request.do_ocr,
        do_table_structure=request.do_table_structure,
        device=request.device,
        ocr_languages=list(request.ocr_languages),
        ocr_engine=request.ocr_engine,
        tessdata_path=request.tessdata_path,
    )

    base = request.source.stem
    out_dir = request.output_dir.resolve()
    artifacts_dir = out_dir / f"{base}-images"
    md_path = out_dir / f"{base}.md"

    extraction = engine.extract(
        request.source,
        markdown_target=md_path,
        artifacts_dir=artifacts_dir,
    )

    formats_set = formats_for(request.formats)
    docx_path: Path | None = None
    pdf_path: Path | None = None

    if "docx" in formats_set:
        docx_path = write_docx(
            extraction.markdown_path,
            out_dir / f"{base}.docx",
            resource_dir=out_dir,
        )
    if "pdf" in formats_set:
        pdf_path = write_pdf(
            extraction.markdown_path,
            out_dir / f"{base}.pdf",
            resource_dir=out_dir,
        )

    return ScanResult(
        source=extraction.source,
        markdown_path=extraction.markdown_path,
        docx_path=docx_path,
        pdf_path=pdf_path,
        images=extraction.images,
        page_count=extraction.page_count,
        artifacts_dir=artifacts_dir,
    )


def scan_batch(
    sources: list[Path],
    output_dir: Path,
    *,
    formats: OutputFormat = OutputFormat.MD,
    do_ocr: bool = True,
    device: str = "auto",
    ocr_languages: tuple[str, ...] = ("pt", "en"),
    ocr_engine: str = "easyocr",
    tessdata_path: str | None = None,
    merge: bool = False,
    merge_name: str = "combined",
) -> BatchResult:
    """Processa múltiplos arquivos reusando uma única instância do engine.

    Quando `merge=True`, ao final concatena todos os MDs em `<merge_name>.md`
    (e `.docx` se solicitado). Os arquivos individuais permanecem.
    """
    if not sources:
        return BatchResult()

    engine = DoclingEngine(
        do_ocr=do_ocr,
        device=device,
        ocr_languages=list(ocr_languages),
        ocr_engine=ocr_engine,
        tessdata_path=tessdata_path,
    )
    result = BatchResult()

    for src in sources:
        try:
            req = ScanRequest(
                source=src,
                output_dir=output_dir,
                formats=formats,
                do_ocr=do_ocr,
                device=device,
                ocr_languages=ocr_languages,
                ocr_engine=ocr_engine,
                tessdata_path=tessdata_path,
            )
            result.successes.append(scan(req, engine=engine))
        except Exception as exc:  # captura amplo: não queremos parar o batch
            log.exception("Falha em %s", src)
            result.failures.append((src, exc))

    if merge and result.successes:
        merge_results(
            result.successes,
            output_dir,
            base_name=merge_name,
            formats=formats,
        )

    return result


def merge_results(
    results: list[ScanResult],
    output_dir: Path,
    *,
    base_name: str = "combined",
    formats: OutputFormat = OutputFormat.MD,
) -> Path:
    """Concatena MDs de múltiplos resultados em um único arquivo.

    Cada seção começa com um heading H2 com o nome da imagem original e um
    separador horizontal antes da próxima. Se `formats` incluir DOCX e/ou
    PDF, também gera os arquivos correspondentes via pandoc.

    Returns:
        Path do MD combinado. DOCX/PDF, se gerados, ficam como
        `<base_name>.docx` e `<base_name>.pdf` no mesmo `output_dir`.
    """
    output_dir = output_dir.resolve()
    target_md = output_dir / f"{base_name}.md"

    parts: list[str] = []
    parts.append(f"# {base_name.replace('-', ' ').title()}\n")
    parts.append(f"*Documento consolidado de {len(results)} imagem(ns).*\n\n")

    for r in sorted(results, key=lambda x: x.source.name):
        parts.append(f"\n---\n\n## {r.source.stem}\n\n")
        # Lê o MD individual e re-escreve sem alterar (paths de imagem ficam relativos)
        try:
            content = r.markdown_path.read_text(encoding="utf-8")
            parts.append(content.lstrip())
        except OSError as exc:
            parts.append(f"*Erro ao ler {r.markdown_path.name}: {exc}*\n")

    target_md.write_text("".join(parts), encoding="utf-8")
    log.info("Merge MD: %s (%d seções)", target_md, len(results))

    formats_set = formats_for(formats)
    if "docx" in formats_set:
        target_docx = output_dir / f"{base_name}.docx"
        write_docx(target_md, target_docx, resource_dir=output_dir)
        log.info("Merge DOCX: %s", target_docx)
    if "pdf" in formats_set:
        target_pdf = output_dir / f"{base_name}.pdf"
        write_pdf(target_md, target_pdf, resource_dir=output_dir)
        log.info("Merge PDF: %s", target_pdf)

    return target_md


def collect_inputs(path: Path) -> list[Path]:
    """Expande um caminho: arquivo único → [arquivo]; pasta → todos os suportados."""
    path = path.resolve()
    if not path.exists():
        raise InvalidInputError(f"Caminho não existe: {path}")
    if path.is_file():
        return [path]
    if path.is_dir():
        files = sorted(
            p for p in path.iterdir()
            if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
        )
        if not files:
            raise InvalidInputError(
                f"Nenhum arquivo suportado em {path}. "
                f"Aceitos: {sorted(SUPPORTED_EXTENSIONS)}"
            )
        return files
    raise InvalidInputError(f"Caminho inválido (não é arquivo nem pasta): {path}")


def _validate_request(request: ScanRequest) -> None:
    if not request.source.exists():
        raise InvalidInputError(f"Source não existe: {request.source}")
    if not request.source.is_file():
        raise InvalidInputError(f"Source não é arquivo: {request.source}")
