"""Layout de paths para jobs e artefatos.

Convenção (spec Section 6):
    <data_dir>/
    ├── scanner.db                       (SQLite)
    └── jobs/
        └── {job_id}/
            ├── inputs/                  (arquivos enviados)
            │   ├── foto1.jpg
            │   └── foto2.jpg
            ├── outputs/                 (MD, DOCX, PDF)
            │   ├── foto1.md
            │   ├── foto1.docx
            │   ├── foto1.pdf
            │   └── combined.md  (se merge)
            ├── images/                  (artifacts extraídos pelo Docling)
            └── .progress.jsonl          (eventos de progresso, append-only)

Helpers retornam Path puros (sem criar nada). Use ensure_*() onde necessário.
"""

from __future__ import annotations

from pathlib import Path


def job_dir(data_dir: Path, job_id: str) -> Path:
    """Diretório raiz de um job: `<data_dir>/jobs/{job_id}/`."""
    return data_dir / "jobs" / job_id


def job_input_path(data_dir: Path, job_id: str, filename: str) -> Path:
    """Path de um arquivo de input: `<data_dir>/jobs/{job_id}/inputs/{filename}`."""
    return job_dir(data_dir, job_id) / "inputs" / filename


def job_output_path(data_dir: Path, job_id: str, filename: str) -> Path:
    """Path de um arquivo de output: `<data_dir>/jobs/{job_id}/outputs/{filename}`."""
    return job_dir(data_dir, job_id) / "outputs" / filename


def job_images_dir(data_dir: Path, job_id: str) -> Path:
    """Pasta de imagens extraídas: `<data_dir>/jobs/{job_id}/images/`."""
    return job_dir(data_dir, job_id) / "images"


def job_progress_path(data_dir: Path, job_id: str) -> Path:
    """Append-only event log: `<data_dir>/jobs/{job_id}/.progress.jsonl`."""
    return job_dir(data_dir, job_id) / ".progress.jsonl"


def ensure_data_dirs(data_dir: Path) -> None:
    """Cria a estrutura mínima do data_dir (idempotente).

    Cria `<data_dir>/` e `<data_dir>/jobs/`. Não cria nada por job —
    use `ensure_job_dirs()` para isso.
    """
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "jobs").mkdir(parents=True, exist_ok=True)


def ensure_job_dirs(data_dir: Path, job_id: str) -> None:
    """Cria todos os subdiretórios de um job (idempotente).

    Cria `inputs/`, `outputs/`, `images/` dentro de `<data_dir>/jobs/{job_id}/`.
    """
    base = job_dir(data_dir, job_id)
    (base / "inputs").mkdir(parents=True, exist_ok=True)
    (base / "outputs").mkdir(parents=True, exist_ok=True)
    (base / "images").mkdir(parents=True, exist_ok=True)
