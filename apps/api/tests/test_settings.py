"""Testes do módulo de settings — Pydantic Settings carrega env vars."""

from __future__ import annotations

from pathlib import Path

import pytest


def test_settings_default_values(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Sem override de env vars, settings tem defaults razoáveis."""
    monkeypatch.setenv("SCANNER_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("SCANNER_VAPID_PUBLIC_KEY", "stub")
    monkeypatch.setenv("SCANNER_VAPID_PRIVATE_KEY", "stub")
    monkeypatch.setenv("SCANNER_VAPID_EMAIL", "test@example.com")
    # Limpa env vars opcionais para garantir defaults
    for opt in ("SCANNER_MAX_WORKERS", "SCANNER_DEVICE", "SCANNER_PURGE_HOURS"):
        monkeypatch.delenv(opt, raising=False)

    from scanner_api.settings import Settings

    s = Settings()  # type: ignore[call-arg]
    assert s.max_workers == 2
    assert s.device == "auto"
    assert s.purge_hours == 72
    assert s.max_upload_mb == 200
    assert s.data_dir == tmp_path


def test_settings_overrides_via_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Env vars sobrescrevem defaults."""
    monkeypatch.setenv("SCANNER_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("SCANNER_MAX_WORKERS", "4")
    monkeypatch.setenv("SCANNER_DEVICE", "cuda")
    monkeypatch.setenv("SCANNER_PURGE_HOURS", "24")
    monkeypatch.setenv("SCANNER_VAPID_PUBLIC_KEY", "stub")
    monkeypatch.setenv("SCANNER_VAPID_PRIVATE_KEY", "stub")
    monkeypatch.setenv("SCANNER_VAPID_EMAIL", "test@example.com")

    from scanner_api.settings import Settings

    s = Settings()  # type: ignore[call-arg]
    assert s.max_workers == 4
    assert s.device == "cuda"
    assert s.purge_hours == 24


def test_settings_requires_vapid_keys(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """VAPID keys são obrigatórias (Field com ...)."""
    for k in ("SCANNER_VAPID_PUBLIC_KEY", "SCANNER_VAPID_PRIVATE_KEY", "SCANNER_VAPID_EMAIL"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("SCANNER_DATA_DIR", str(tmp_path))

    from pydantic import ValidationError

    from scanner_api.settings import Settings

    with pytest.raises(ValidationError, match="vapid"):
        Settings()  # type: ignore[call-arg]


def test_settings_db_path_derived_from_data_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """db_path é sempre `<data_dir>/scanner.db`."""
    monkeypatch.setenv("SCANNER_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("SCANNER_VAPID_PUBLIC_KEY", "stub")
    monkeypatch.setenv("SCANNER_VAPID_PRIVATE_KEY", "stub")
    monkeypatch.setenv("SCANNER_VAPID_EMAIL", "test@example.com")

    from scanner_api.settings import Settings

    s = Settings()  # type: ignore[call-arg]
    assert s.db_path == tmp_path / "scanner.db"
    assert s.jobs_dir == tmp_path / "jobs"
    assert s.db_url == f"sqlite+aiosqlite:///{tmp_path / 'scanner.db'}"


def test_settings_validates_device_pattern(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """device aceita apenas auto|cuda|cpu (Field pattern)."""
    monkeypatch.setenv("SCANNER_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("SCANNER_DEVICE", "tpu")  # inválido
    monkeypatch.setenv("SCANNER_VAPID_PUBLIC_KEY", "stub")
    monkeypatch.setenv("SCANNER_VAPID_PRIVATE_KEY", "stub")
    monkeypatch.setenv("SCANNER_VAPID_EMAIL", "test@example.com")

    from pydantic import ValidationError

    from scanner_api.settings import Settings

    with pytest.raises(ValidationError):
        Settings()  # type: ignore[call-arg]


def test_get_settings_is_singleton(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """get_settings retorna a mesma instância via lru_cache."""
    monkeypatch.setenv("SCANNER_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("SCANNER_VAPID_PUBLIC_KEY", "stub")
    monkeypatch.setenv("SCANNER_VAPID_PRIVATE_KEY", "stub")
    monkeypatch.setenv("SCANNER_VAPID_EMAIL", "test@example.com")

    from scanner_api.settings import get_settings

    get_settings.cache_clear()  # reset por causa de outros testes
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2
