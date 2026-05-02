"""Configuração via env vars (Pydantic Settings).

Carrega variáveis de ambiente prefixadas com SCANNER_. Override em testes via
monkeypatch.setenv. Em produção, vem do `docker-compose.yml` (env_file ou
`environment:`).

Spec ref: docs/superpowers/specs/2026-05-02-web-app-pwa-design.md Seção 7.5
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuração imutável da aplicação (carregada do ambiente).

    Todas as variáveis prefixadas com `SCANNER_` (ex: `SCANNER_DATA_DIR`).
    """

    model_config = SettingsConfigDict(
        env_prefix="SCANNER_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Storage
    data_dir: Path = Field(
        default=Path("/data"),
        description="Raiz para jobs e DB. Default /data (volume Docker em prod).",
    )

    # Workers / OCR
    max_workers: int = Field(
        default=2,
        ge=1,
        le=8,
        description="ProcessPoolExecutor size. 2 é seguro em VPS 16GB.",
    )
    device: str = Field(
        default="auto",
        pattern="^(auto|cuda|cpu)$",
        description="Inferência: auto detecta GPU, cuda força, cpu desativa.",
    )

    # Retention
    purge_hours: int = Field(
        default=72,
        ge=1,
        description="TTL de jobs não-favoritados (horas).",
    )

    # Upload limits
    max_upload_mb: int = Field(
        default=200,
        ge=1,
        description="Limite por request multipart (MB).",
    )

    # VAPID (push notifications) — obrigatórios
    vapid_public_key: str = Field(
        ...,
        min_length=1,
        description="VAPID public key (base64url) — gerada uma vez via "
        "infra/scripts/generate_vapid_keys.py",
    )
    vapid_private_key: str = Field(
        ...,
        min_length=1,
        description="VAPID private key (base64url) — secreto.",
    )
    vapid_email: str = Field(
        ...,
        min_length=3,
        description="Email de contato para Mozilla/Google push services.",
    )

    # Public URL (para CORS, push subject)
    api_base_url: str = Field(
        default="http://localhost:8000",
        description="URL pública da API (usada em CORS allowlist em prod).",
    )

    # Computed properties

    @property
    def db_path(self) -> Path:
        """Caminho do SQLite, sempre dentro do data_dir."""
        return self.data_dir / "scanner.db"

    @property
    def jobs_dir(self) -> Path:
        """Pasta raiz dos jobs (`<data_dir>/jobs/`)."""
        return self.data_dir / "jobs"

    @property
    def db_url(self) -> str:
        """SQLAlchemy URL — async driver aiosqlite."""
        return f"sqlite+aiosqlite:///{self.db_path}"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Singleton — settings é imutável, carrega 1 vez.

    Em testes, limpe via `get_settings.cache_clear()` entre fixtures que
    mexem em env vars.
    """
    return Settings()  # type: ignore[call-arg]
