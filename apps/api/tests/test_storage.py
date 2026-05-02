"""Testes do storage layout — paths e ensure_dir."""

from __future__ import annotations

from pathlib import Path

from scanner_api.storage import (
    ensure_data_dirs,
    ensure_job_dirs,
    job_dir,
    job_images_dir,
    job_input_path,
    job_output_path,
    job_progress_path,
)


def test_job_dir_is_under_data_dir(tmp_path: Path) -> None:
    """job_dir(data, id) → <data>/jobs/<id>/"""
    expected = tmp_path / "jobs" / "abc-123"
    assert job_dir(tmp_path, "abc-123") == expected


def test_job_input_path_is_inside_job_dir(tmp_path: Path) -> None:
    """job_input_path retorna <data>/jobs/<id>/inputs/<filename>"""
    p = job_input_path(tmp_path, "abc-123", "foto.jpg")
    assert p == tmp_path / "jobs" / "abc-123" / "inputs" / "foto.jpg"


def test_job_output_path(tmp_path: Path) -> None:
    """job_output_path retorna <data>/jobs/<id>/outputs/<filename>"""
    p = job_output_path(tmp_path, "abc-123", "result.md")
    assert p == tmp_path / "jobs" / "abc-123" / "outputs" / "result.md"


def test_job_images_dir(tmp_path: Path) -> None:
    """job_images_dir retorna <data>/jobs/<id>/images"""
    assert job_images_dir(tmp_path, "abc-123") == (
        tmp_path / "jobs" / "abc-123" / "images"
    )


def test_job_progress_path(tmp_path: Path) -> None:
    """job_progress_path retorna <data>/jobs/<id>/.progress.jsonl"""
    p = job_progress_path(tmp_path, "abc-123")
    assert p == tmp_path / "jobs" / "abc-123" / ".progress.jsonl"


def test_ensure_data_dirs_creates_layout(tmp_path: Path) -> None:
    """ensure_data_dirs cria <data>/ e <data>/jobs/."""
    data = tmp_path / "fresh"
    ensure_data_dirs(data)
    assert data.is_dir()
    assert (data / "jobs").is_dir()


def test_ensure_data_dirs_idempotent(tmp_path: Path) -> None:
    """Chamar ensure_data_dirs duas vezes não levanta."""
    data = tmp_path / "fresh"
    ensure_data_dirs(data)
    ensure_data_dirs(data)  # não levanta


def test_ensure_job_dirs_creates_subdirs(tmp_path: Path) -> None:
    """ensure_job_dirs cria inputs/, outputs/, images/."""
    ensure_data_dirs(tmp_path)
    ensure_job_dirs(tmp_path, "job-xyz")
    base = tmp_path / "jobs" / "job-xyz"
    assert (base / "inputs").is_dir()
    assert (base / "outputs").is_dir()
    assert (base / "images").is_dir()


def test_ensure_job_dirs_idempotent(tmp_path: Path) -> None:
    """ensure_job_dirs pode ser chamado duas vezes sem erro."""
    ensure_data_dirs(tmp_path)
    ensure_job_dirs(tmp_path, "job-xyz")
    ensure_job_dirs(tmp_path, "job-xyz")  # não levanta


def test_storage_paths_are_pure_no_io(tmp_path: Path) -> None:
    """Helpers de path NÃO criam nada no filesystem (são puros)."""
    job_id = "should-not-exist"
    _ = job_dir(tmp_path, job_id)
    _ = job_input_path(tmp_path, job_id, "x.jpg")
    _ = job_output_path(tmp_path, job_id, "x.md")
    _ = job_images_dir(tmp_path, job_id)
    _ = job_progress_path(tmp_path, job_id)
    # Nenhuma pasta deve ter sido criada
    assert not (tmp_path / "jobs").exists()
