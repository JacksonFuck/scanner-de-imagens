"""Entry point do worker subprocess.

Cada subprocess do ProcessPoolExecutor:
1. Importa Docling/scanner UMA VEZ por subprocess (caro, ~5s)
2. Recebe job_id + paths de input/output via dict serializável
3. Roda scanner.scan_batch()
4. Apenda eventos no <job>/.progress.jsonl

Não conecta no DB diretamente — atualiza status via parent process após
retornar (callback no `pool._on_job_done`).
"""

from __future__ import annotations

import json
import time
import traceback
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class WorkerJobSpec:
    """Tudo que o worker precisa para processar (sem ORM)."""

    job_id: str
    inputs: list[Path]
    output_dir: Path
    progress_path: Path
    formats: str  # 'md' | 'docx' | 'pdf' | 'all' | 'both'
    merge: bool = False
    do_ocr: bool = True
    do_tables: bool = True
    device: str = "auto"
    ocr_engine: str = "easyocr"
    ocr_languages: tuple[str, ...] = ("pt", "en")


@dataclass
class WorkerResult:
    """Resumo do processamento, lido pelo parent após o worker retornar."""

    job_id: str
    status: str  # 'done' | 'error'
    output_files: list[tuple[str, str, int]] = field(default_factory=list)
    page_count: int = 0
    error_msg: str | None = None


def _emit(progress_path: Path, event: dict) -> None:
    """Append-only writer para .progress.jsonl (uma linha JSON por evento)."""
    progress_path.parent.mkdir(parents=True, exist_ok=True)
    with progress_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


def _spec_from_dict(spec_dict: dict) -> WorkerJobSpec:
    """Reconstrói WorkerJobSpec do dict serializado (paths como str)."""
    return WorkerJobSpec(
        job_id=spec_dict["job_id"],
        inputs=[Path(p) for p in spec_dict["inputs"]],
        output_dir=Path(spec_dict["output_dir"]),
        progress_path=Path(spec_dict["progress_path"]),
        formats=spec_dict["formats"],
        merge=spec_dict.get("merge", False),
        do_ocr=spec_dict.get("do_ocr", True),
        do_tables=spec_dict.get("do_tables", True),
        device=spec_dict.get("device", "auto"),
        ocr_engine=spec_dict.get("ocr_engine", "easyocr"),
        ocr_languages=tuple(spec_dict.get("ocr_languages", ("pt", "en"))),
    )


def process_job(spec_dict: dict) -> dict:
    """Entry point chamado via run_in_executor.

    Recebe dict (serializável cross-process) e retorna dict.
    """
    spec = _spec_from_dict(spec_dict)

    _emit(
        spec.progress_path,
        {"type": "started", "ts": time.time(), "input_count": len(spec.inputs)},
    )

    try:
        # Lazy imports — pesados, só uma vez por subprocess
        from scanner.pipeline import OutputFormat, scan_batch

        fmt_map: dict[str, OutputFormat] = {
            "md": OutputFormat.MD,
            "docx": OutputFormat.DOCX,
            "pdf": OutputFormat.PDF,
            "all": OutputFormat.ALL,
            "both": OutputFormat.BOTH,
        }
        if spec.formats not in fmt_map:
            raise ValueError(f"Formato inválido: {spec.formats}")

        # Cria output_dir se não existir
        spec.output_dir.mkdir(parents=True, exist_ok=True)

        result = scan_batch(
            spec.inputs,
            spec.output_dir,
            formats=fmt_map[spec.formats],
            do_ocr=spec.do_ocr,
            device=spec.device,
            ocr_languages=spec.ocr_languages,
            ocr_engine=spec.ocr_engine,
            merge=spec.merge,
        )

        # Emite evento por arquivo concluído (progresso granular)
        for i, sr in enumerate(result.successes, 1):
            _emit(
                spec.progress_path,
                {
                    "type": "progress",
                    "ts": time.time(),
                    "current": i,
                    "total": len(spec.inputs),
                    "current_file": sr.source.name,
                },
            )

        # Coleta arquivos gerados
        output_files: list[tuple[str, str, int]] = []
        for sr in result.successes:
            md_size = sr.markdown_path.stat().st_size if sr.markdown_path.exists() else 0
            output_files.append(("output_md", sr.markdown_path.name, md_size))
            if sr.docx_path and sr.docx_path.exists():
                output_files.append(
                    ("output_docx", sr.docx_path.name, sr.docx_path.stat().st_size)
                )
            if sr.pdf_path and sr.pdf_path.exists():
                output_files.append(
                    ("output_pdf", sr.pdf_path.name, sr.pdf_path.stat().st_size)
                )
            for img in sr.images:
                if img.exists():
                    output_files.append(("image", img.name, img.stat().st_size))

        page_count = sum(sr.page_count for sr in result.successes)

        # Falhas no batch (parciais) viram error_msg
        error_msg: str | None = None
        if result.failures:
            error_msg = "; ".join(
                f"{src.name}: {exc}" for src, exc in result.failures
            )

        wr = WorkerResult(
            job_id=spec.job_id,
            status="done" if not error_msg else "error",
            output_files=output_files,
            page_count=page_count,
            error_msg=error_msg,
        )
        _emit(
            spec.progress_path,
            {
                "type": "done" if wr.status == "done" else "error",
                "ts": time.time(),
                "page_count": page_count,
                "message": error_msg,
            },
        )

    except Exception as exc:
        # Última linha de defesa: qualquer crash vira WorkerResult com status=error
        tb = traceback.format_exc()
        wr = WorkerResult(
            job_id=spec.job_id,
            status="error",
            error_msg=f"{exc}\n{tb}",
        )
        _emit(
            spec.progress_path,
            {"type": "error", "ts": time.time(), "message": str(exc)},
        )

    return asdict(wr)
