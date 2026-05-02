"""Orquestrador — costura ingest → engine → exports.

Função pública `scan()` é o ponto de entrada usado pela CLI e por testes.
Toda a complexidade fica aqui; a CLI é só apresentação.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

from scanner.engine.docling_engine import SUPPORTED_EXTENSIONS, DoclingEngine
from scanner.errors import InvalidInputError
from scanner.export import write_docx

log = logging.getLogger(__name__)


class OutputFormat(StrEnum):
    """Formatos de saída solicitáveis."""

    MD = "md"
    DOCX = "docx"
    BOTH = "both"


@dataclass(slots=True)
class ScanRequest:
    """Pedido de scan — input + onde gravar + o que produzir."""

    source: Path
    output_dir: Path
    formats: OutputFormat = OutputFormat.MD
    do_ocr: bool = True
    do_table_structure: bool = True
    device: str = "auto"  # 'auto' | 'cuda' | 'cpu'


@dataclass(slots=True)
class ScanResult:
    """Resultado: caminhos dos arquivos gerados."""

    source: Path
    markdown_path: Path
    docx_path: Path | None
    images: tuple[Path, ...]
    page_count: int
    artifacts_dir: Path

    def __str__(self) -> str:
        parts = [f"  - {self.markdown_path}"]
        if self.docx_path:
            parts.append(f"  - {self.docx_path}")
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

    docx_path: Path | None = None
    if request.formats in (OutputFormat.DOCX, OutputFormat.BOTH):
        docx_path = write_docx(extraction.markdown_path, out_dir / f"{base}.docx", resource_dir=out_dir)

    return ScanResult(
        source=extraction.source,
        markdown_path=extraction.markdown_path,
        docx_path=docx_path,
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
) -> BatchResult:
    """Processa múltiplos arquivos reusando uma única instância do engine."""
    if not sources:
        return BatchResult()

    engine = DoclingEngine(do_ocr=do_ocr, device=device)
    result = BatchResult()

    for src in sources:
        try:
            req = ScanRequest(
                source=src,
                output_dir=output_dir,
                formats=formats,
                do_ocr=do_ocr,
                device=device,
            )
            result.successes.append(scan(req, engine=engine))
        except Exception as exc:  # captura amplo: não queremos parar o batch
            log.exception("Falha em %s", src)
            result.failures.append((src, exc))

    return result


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
