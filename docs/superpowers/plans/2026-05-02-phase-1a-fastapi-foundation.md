# Phase 1A — FastAPI Backend Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar o esqueleto do backend FastAPI em `apps/api/` com configuração, storage, banco SQLite, ORM models e endpoint `/api/health` funcional. **Não inclui** workers/jobs/WebSocket/push — esses ficam para Phase 1B/1C.

**Architecture:** FastAPI 0.115+ com lifespan async. Pydantic Settings para configuração via env vars. SQLAlchemy 2.0 ORM com SQLite. Alembic para migrações. Estrutura monorepo: `apps/api/` consome `src/scanner/` como dep local.

**Tech Stack:** Python 3.11+, FastAPI, Uvicorn, Pydantic v2 + pydantic-settings, SQLAlchemy 2.0, Alembic, aiofiles, pytest, httpx (test client), ruff.

**Source spec:** `docs/superpowers/specs/2026-05-02-web-app-pwa-design.md` (commit `1129ce8`), Seção 6 (estrutura) + Seção 7.3 (DB schema) + Seção 7.5 (env vars).

**Working directory:** `c:\Users\jacks\OneDrive\2º Cérebro\Scanner de imagens`

**Pré-requisito:** Phase 0 mergeada ou disponível (CLI, postprocess, PDF export funcionando). Branch base: `master` (após merge da Phase 0) ou `feat/phase-0-backend-refactor`.

---

## File Structure

| Caminho | Ação | Responsabilidade |
|---------|------|------------------|
| `apps/api/pyproject.toml` | CREATE | Dependências do backend (fastapi, sqlalchemy, alembic, etc.) + dep local de scanner/ |
| `apps/api/Dockerfile` | CREATE | Multistage build: python-slim + scanner + api + texlive-xetex + pandoc |
| `apps/api/.dockerignore` | CREATE | Exclui __pycache__, .venv, etc |
| `apps/api/src/scanner_api/__init__.py` | CREATE | Versão do API + re-exports |
| `apps/api/src/scanner_api/main.py` | CREATE | FastAPI app + lifespan (startup/shutdown) + CORS |
| `apps/api/src/scanner_api/settings.py` | CREATE | Pydantic Settings (todas env vars do spec 7.5) |
| `apps/api/src/scanner_api/storage.py` | CREATE | Paths, ensure_dir, layout `/data/jobs/{id}/` |
| `apps/api/src/scanner_api/db/__init__.py` | CREATE | Re-export engine + session factory |
| `apps/api/src/scanner_api/db/engine.py` | CREATE | SQLAlchemy engine + sessionmaker assíncrono |
| `apps/api/src/scanner_api/db/models.py` | CREATE | Job, JobFile, PushSubscription ORM (mapeia spec 7.3) |
| `apps/api/src/scanner_api/db/schema.sql` | CREATE | DDL canônico (referência humana, espelha o ORM) |
| `apps/api/alembic.ini` | CREATE | Configuração Alembic |
| `apps/api/src/scanner_api/db/migrations/env.py` | CREATE | Hook do Alembic |
| `apps/api/src/scanner_api/db/migrations/versions/0001_initial.py` | CREATE | Primeira migração (3 tabelas + índices) |
| `apps/api/src/scanner_api/routes/__init__.py` | CREATE | Re-export de routers |
| `apps/api/src/scanner_api/routes/health.py` | CREATE | GET /api/health (device, queue, db, disk) |
| `apps/api/tests/conftest.py` | CREATE | Fixtures: tmp_data_dir, test_client (httpx async), test_db |
| `apps/api/tests/test_settings.py` | CREATE | Settings load/override via env |
| `apps/api/tests/test_storage.py` | CREATE | Path layout + ensure_dir |
| `apps/api/tests/test_db_models.py` | CREATE | ORM mapping + relationship + cascade |
| `apps/api/tests/test_health.py` | CREATE | GET /api/health retorna JSON com campos esperados |

---

## Task 1: Backend skeleton + minimal FastAPI app

**Files:**
- Create: `apps/api/pyproject.toml`
- Create: `apps/api/Dockerfile`
- Create: `apps/api/.dockerignore`
- Create: `apps/api/src/scanner_api/__init__.py`
- Create: `apps/api/src/scanner_api/main.py`
- Create: `apps/api/tests/__init__.py`
- Create: `apps/api/tests/conftest.py`

- [ ] **Step 1.1: Criar `apps/api/pyproject.toml`**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "scanner-api"
version = "0.1.0"
description = "FastAPI backend for Scanner de Imagens — exposes scanner pipeline as web API"
readme = "README.md"
requires-python = ">=3.11"
license = { text = "MIT" }
authors = [{ name = "Jackson", email = "jacksontorax@gmail.com" }]

dependencies = [
    # FastAPI core
    "fastapi>=0.115",
    "uvicorn[standard]>=0.32",
    # Validação + settings
    "pydantic>=2.9",
    "pydantic-settings>=2.6",
    # ORM + migrations
    "sqlalchemy>=2.0",
    "alembic>=1.14",
    # File IO
    "aiofiles>=24",
    "python-multipart>=0.0.20",  # form upload
    # Push notifications (Phase 1C usa, mas declaramos cedo)
    "pywebpush>=2.0",
    # Scanner package: dep local em path relativo
    "scanner-de-imagens",
]

[project.optional-dependencies]
dev = [
    "pytest>=8",
    "pytest-asyncio>=0.24",
    "pytest-cov>=5",
    "httpx>=0.28",
    "ruff>=0.6",
    "mypy>=1.10",
]

[tool.uv.sources]
scanner-de-imagens = { path = "../..", editable = true }

[tool.hatch.build.targets.wheel]
packages = ["src/scanner_api"]

[tool.ruff]
line-length = 100
target-version = "py311"
src = ["src", "tests"]

[tool.ruff.lint]
select = ["E", "F", "W", "I", "B", "UP", "SIM", "RUF"]
ignore = ["E501"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra --strict-markers"
asyncio_mode = "auto"
markers = ["slow: tests that load Docling models"]
```

- [ ] **Step 1.2: Criar `apps/api/src/scanner_api/__init__.py`**

```python
"""Scanner de Imagens — FastAPI backend.

Exposes the scanner OCR pipeline as a single-tenant web API with async jobs,
WebSocket progress, and push notifications. Reuses src/scanner/ as a library
(no fork of OCR logic).
"""

from __future__ import annotations

__version__ = "0.1.0"
```

- [ ] **Step 1.3: Criar `apps/api/src/scanner_api/main.py` (stub mínimo)**

```python
"""FastAPI application — entry point para Uvicorn.

Lifespan async para inicialização (worker pool em Phase 1B). CORS aberto
para o frontend Next.js. Routes são montadas via include_router.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from scanner_api import __version__

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup/shutdown hooks.

    Phase 1A: apenas log + placeholder. Phase 1B adiciona ProcessPoolExecutor.
    """
    log.info("scanner_api %s startup", __version__)
    yield
    log.info("scanner_api %s shutdown", __version__)


def create_app() -> FastAPI:
    """Factory para criar a app — facilita testes (cria app por test client)."""
    app = FastAPI(
        title="Scanner de Imagens API",
        version=__version__,
        description="OCR de fotos de páginas → Markdown + DOCX + PDF",
        lifespan=lifespan,
    )

    # CORS: permitir o frontend Next.js (mesmo domínio em prod via Nginx)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # ajustado em produção via env var
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routes vão ser montados aqui em Phase 1A Task 6 + Phase 1B
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "scanner_api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
```

- [ ] **Step 1.4: Criar `apps/api/Dockerfile`**

```dockerfile
# syntax=docker/dockerfile:1.7

FROM python:3.13-slim AS base

# Dependências de sistema:
# - pandoc + texlive-xetex para PDF export
# - tesseract-ocr-por para OCR fallback (se EasyOCR falhar)
# - libgl1 para opencv (dep transitiva do Docling)
RUN apt-get update && apt-get install -y --no-install-recommends \
    pandoc \
    texlive-xetex \
    texlive-fonts-recommended \
    texlive-lang-portuguese \
    tesseract-ocr-por \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia o monorepo (scanner/ + apps/api/)
COPY pyproject.toml ./
COPY src ./src
COPY apps/api ./apps/api

# Instala scanner core + api
RUN pip install --no-cache-dir -e . \
    && pip install --no-cache-dir -e ./apps/api

EXPOSE 8000

CMD ["uvicorn", "scanner_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 1.5: Criar `apps/api/.dockerignore`**

```
__pycache__/
*.py[cod]
*$py.class
.venv/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/
node_modules/
.next/
.git/
docling-main/
output/
data/
graphify-out/
```

- [ ] **Step 1.6: Criar `apps/api/tests/conftest.py` (fixtures básicas)**

```python
"""Fixtures compartilhadas dos testes do scanner_api."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator, Iterator
from pathlib import Path

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def tmp_data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Cria um data dir temporário e seta SCANNER_DATA_DIR para apontar lá."""
    data = tmp_path / "data"
    data.mkdir()
    monkeypatch.setenv("SCANNER_DATA_DIR", str(data))
    return data


@pytest.fixture
def app(tmp_data_dir: Path) -> Iterator[FastAPI]:
    """Cria uma instância nova da app por test (lifespan correto)."""
    from scanner_api.main import create_app

    yield create_app()


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    """httpx AsyncClient apontado para a app em ASGI mode."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
```

- [ ] **Step 1.7: Smoke test — pode importar e instanciar?**

Run:
```bash
cd apps/api
/c/Users/jacks/scoop/apps/python/current/python.exe -m pip install -e . 2>&1 | tail -3
/c/Users/jacks/scoop/apps/python/current/python.exe -c "from scanner_api.main import create_app; app = create_app(); print('OK', app.title)"
```

Expected: `OK Scanner de Imagens API`.

- [ ] **Step 1.8: Commit**

```bash
cd ..  # voltar para repo root
git add apps/api/
git commit -m "feat(api): bootstrap FastAPI backend skeleton

- apps/api/pyproject.toml: deps fastapi/sqlalchemy/pydantic-settings/aiofiles
- main.py: create_app() factory + lifespan async + CORS
- Dockerfile: python:3.13-slim + pandoc + texlive-xetex + tesseract
- conftest.py: fixtures tmp_data_dir, app, client (httpx ASGI)
- Sem rotas ainda — Phase 1A Task 6 adiciona /api/health

Plan: docs/superpowers/plans/2026-05-02-phase-1a-fastapi-foundation.md (Task 1/6)"
```

---

## Task 2: Settings module (Pydantic Settings)

**Files:**
- Create: `apps/api/src/scanner_api/settings.py`
- Create: `apps/api/tests/test_settings.py`

- [ ] **Step 2.1: Escrever testes primeiro**

```python
# apps/api/tests/test_settings.py
"""Testes do módulo de settings — Pydantic Settings carrega env vars."""

from __future__ import annotations

from pathlib import Path

import pytest


def test_settings_default_values(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Sem env vars, settings tem defaults razoáveis."""
    monkeypatch.setenv("SCANNER_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("SCANNER_VAPID_PUBLIC_KEY", "stub")
    monkeypatch.setenv("SCANNER_VAPID_PRIVATE_KEY", "stub")
    monkeypatch.setenv("SCANNER_VAPID_EMAIL", "test@example.com")

    from scanner_api.settings import Settings

    s = Settings()
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

    s = Settings()
    assert s.max_workers == 4
    assert s.device == "cuda"
    assert s.purge_hours == 24


def test_settings_requires_vapid_keys(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """VAPID keys são obrigatórias (push notifications)."""
    # Garante que NENHUMA das vars VAPID está setada
    for k in ("SCANNER_VAPID_PUBLIC_KEY", "SCANNER_VAPID_PRIVATE_KEY", "SCANNER_VAPID_EMAIL"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("SCANNER_DATA_DIR", str(tmp_path))

    from pydantic import ValidationError

    from scanner_api.settings import Settings

    with pytest.raises(ValidationError, match="vapid"):
        Settings()


def test_settings_db_path_derived_from_data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """db_path é sempre `<data_dir>/scanner.db`."""
    monkeypatch.setenv("SCANNER_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("SCANNER_VAPID_PUBLIC_KEY", "stub")
    monkeypatch.setenv("SCANNER_VAPID_PRIVATE_KEY", "stub")
    monkeypatch.setenv("SCANNER_VAPID_EMAIL", "test@example.com")

    from scanner_api.settings import Settings

    s = Settings()
    assert s.db_path == tmp_path / "scanner.db"
```

- [ ] **Step 2.2: Rodar testes — confirm fail**

Run: `cd apps/api && pytest tests/test_settings.py -v`
Expected: FAIL — `ModuleNotFoundError: scanner_api.settings`.

- [ ] **Step 2.3: Implementar `apps/api/src/scanner_api/settings.py`**

```python
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
    """Configuração imutável da aplicação (carregada do ambiente)."""

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
        description="Raiz para jobs e DB. Default /data (volume Docker).",
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
    """Singleton — settings é imutável, carrega 1 vez."""
    return Settings()  # type: ignore[call-arg]
```

- [ ] **Step 2.4: Adicionar dep `aiosqlite` ao pyproject.toml**

Editar `apps/api/pyproject.toml`, adicionar em `dependencies`:

```toml
    "aiosqlite>=0.20",  # async driver para SQLite via SQLAlchemy
```

Reinstalar: `pip install -e ./apps/api`

- [ ] **Step 2.5: Rodar testes — verde**

Run: `cd apps/api && pytest tests/test_settings.py -v`
Expected: 4 testes PASS.

- [ ] **Step 2.6: Commit**

```bash
git add apps/api/src/scanner_api/settings.py apps/api/tests/test_settings.py apps/api/pyproject.toml
git commit -m "feat(api): add Settings module via Pydantic Settings

- All env vars prefixed SCANNER_ (per spec Section 7.5)
- VAPID keys são obrigatórias (raises ValidationError se ausentes)
- Computed properties: db_path, jobs_dir, db_url (sqlite+aiosqlite)
- Validators: device pattern, max_workers ge=1 le=8, purge_hours ge=1
- get_settings() singleton via lru_cache
- 4 tests cobrindo defaults, overrides, validação, computed paths

Plan: docs/superpowers/plans/2026-05-02-phase-1a-fastapi-foundation.md (Task 2/6)"
```

---

## Task 3: Storage helper

**Files:**
- Create: `apps/api/src/scanner_api/storage.py`
- Create: `apps/api/tests/test_storage.py`

- [ ] **Step 3.1: Tests primeiro**

```python
# apps/api/tests/test_storage.py
"""Testes do storage layout — paths e ensure_dir."""

from __future__ import annotations

from pathlib import Path

import pytest

from scanner_api.storage import (
    ensure_data_dirs,
    job_dir,
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


def test_job_progress_path(tmp_path: Path) -> None:
    """job_progress_path retorna <data>/jobs/<id>/.progress.jsonl"""
    p = job_progress_path(tmp_path, "abc-123")
    assert p == tmp_path / "jobs" / "abc-123" / ".progress.jsonl"


def test_ensure_data_dirs_creates_layout(tmp_path: Path) -> None:
    """ensure_data_dirs cria <data>/jobs/ e parent do db."""
    data = tmp_path / "fresh"
    ensure_data_dirs(data)
    assert (data / "jobs").is_dir()
    assert data.is_dir()


def test_ensure_data_dirs_idempotent(tmp_path: Path) -> None:
    """Chamar ensure_data_dirs duas vezes não levanta."""
    data = tmp_path / "fresh"
    ensure_data_dirs(data)
    ensure_data_dirs(data)  # não levanta
```

- [ ] **Step 3.2: Run, fail, implement**

Run: `cd apps/api && pytest tests/test_storage.py -v`
Expected: FAIL.

Implementar `apps/api/src/scanner_api/storage.py`:

```python
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

Helpers retornam Path puros (sem criar nada). Use ensure_dir() onde necessário.
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
    """Cria a estrutura mínima do data_dir (idempotente)."""
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "jobs").mkdir(parents=True, exist_ok=True)


def ensure_job_dirs(data_dir: Path, job_id: str) -> None:
    """Cria todos os subdiretórios de um job (idempotente)."""
    base = job_dir(data_dir, job_id)
    (base / "inputs").mkdir(parents=True, exist_ok=True)
    (base / "outputs").mkdir(parents=True, exist_ok=True)
    (base / "images").mkdir(parents=True, exist_ok=True)
```

- [ ] **Step 3.3: Run tests — verde**

Expected: 6 testes PASS.

- [ ] **Step 3.4: Commit**

```bash
git add apps/api/src/scanner_api/storage.py apps/api/tests/test_storage.py
git commit -m "feat(api): add storage layout helpers

- job_dir / job_input_path / job_output_path / job_images_dir / job_progress_path
- ensure_data_dirs (root) e ensure_job_dirs (per job)
- Layout ref: spec Section 6 (data/jobs/{id}/{inputs,outputs,images,.progress.jsonl})
- 6 testes cobrindo path computation + idempotência"
```

---

## Task 4: SQLAlchemy engine + session factory

**Files:**
- Create: `apps/api/src/scanner_api/db/__init__.py`
- Create: `apps/api/src/scanner_api/db/engine.py`

- [ ] **Step 4.1: Implementar `apps/api/src/scanner_api/db/__init__.py`**

```python
"""DB layer: SQLAlchemy 2.0 async + SQLite via aiosqlite."""

from __future__ import annotations

from scanner_api.db.engine import async_session_factory, get_engine, get_session

__all__ = ["async_session_factory", "get_engine", "get_session"]
```

- [ ] **Step 4.2: Implementar `apps/api/src/scanner_api/db/engine.py`**

```python
"""SQLAlchemy 2.0 engine + session factory (async via aiosqlite).

A engine é singleton e criada lazy via `get_engine()`. As sessions são curtas:
abertas por request via dependency `get_session()`.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from scanner_api.settings import get_settings


@lru_cache(maxsize=1)
def get_engine() -> AsyncEngine:
    """Singleton: cria a engine ao primeiro uso."""
    settings = get_settings()
    return create_async_engine(
        settings.db_url,
        echo=False,  # True para debug local
        future=True,
        # SQLite específico: 1 conexão por path; async é cooperativo
        connect_args={"check_same_thread": False},
    )


@lru_cache(maxsize=1)
def async_session_factory() -> async_sessionmaker[AsyncSession]:
    """Factory de sessions assíncronas, vinculada à engine singleton."""
    return async_sessionmaker(
        get_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency: cede uma session por request, encerra ao fim."""
    factory = async_session_factory()
    async with factory() as session:
        yield session
```

- [ ] **Step 4.3: Smoke test rápido**

Run via `python -c`:
```bash
cd apps/api
/c/Users/jacks/scoop/apps/python/current/python.exe -c "
import os, tempfile
with tempfile.TemporaryDirectory() as d:
    os.environ['SCANNER_DATA_DIR'] = d
    os.environ['SCANNER_VAPID_PUBLIC_KEY'] = 'stub'
    os.environ['SCANNER_VAPID_PRIVATE_KEY'] = 'stub'
    os.environ['SCANNER_VAPID_EMAIL'] = 't@e.com'
    from scanner_api.db import get_engine
    eng = get_engine()
    print('OK', eng.url)
"
```

Expected: `OK sqlite+aiosqlite:///<tmp>/scanner.db`.

- [ ] **Step 4.4: Commit**

```bash
git add apps/api/src/scanner_api/db/__init__.py apps/api/src/scanner_api/db/engine.py
git commit -m "feat(api): add SQLAlchemy 2.0 async engine + session factory

- get_engine() singleton via lru_cache
- async_session_factory() vinculado à engine
- get_session() dependency para FastAPI (yield session, close on exit)
- Driver: sqlite+aiosqlite (cooperativo async)"
```

---

## Task 5: ORM models + Alembic init + first migration

**Files:**
- Create: `apps/api/src/scanner_api/db/models.py`
- Create: `apps/api/src/scanner_api/db/schema.sql` (referência humana)
- Create: `apps/api/alembic.ini`
- Create: `apps/api/src/scanner_api/db/migrations/env.py`
- Create: `apps/api/src/scanner_api/db/migrations/versions/0001_initial.py`
- Create: `apps/api/tests/test_db_models.py`

- [ ] **Step 5.1: Tests primeiro**

```python
# apps/api/tests/test_db_models.py
"""Testes dos ORM models — mapping, relationship, cascade."""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from scanner_api.db.models import Base, Job, JobFile, PushSubscription


@pytest.fixture
async def session(tmp_data_dir):
    """Engine in-memory para isolamento de testes."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    from sqlalchemy.ext.asyncio import async_sessionmaker
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        yield s
    await engine.dispose()


async def test_job_can_be_created(session: AsyncSession) -> None:
    """Um Job pode ser inserido e recuperado."""
    job = Job(
        id="job-1",
        status="queued",
        title="test",
        input_count=2,
        merge_mode=1,
        formats="all",
    )
    session.add(job)
    await session.commit()

    fetched = await session.get(Job, "job-1")
    assert fetched is not None
    assert fetched.title == "test"
    assert fetched.input_count == 2
    assert fetched.merge_mode == 1


async def test_job_files_cascade_delete(session: AsyncSession) -> None:
    """Deletar Job apaga JobFile relacionados (cascade)."""
    job = Job(id="job-2", status="queued", input_count=1, merge_mode=0, formats="md")
    job.files.append(JobFile(role="input", filename="foto.jpg", size_bytes=1000))
    session.add(job)
    await session.commit()

    await session.delete(job)
    await session.commit()

    from sqlalchemy import select
    result = await session.execute(select(JobFile))
    assert result.scalars().all() == []


async def test_push_subscription_unique_endpoint(session: AsyncSession) -> None:
    """endpoint é PRIMARY KEY — não pode duplicar."""
    s1 = PushSubscription(endpoint="https://example.com/1", p256dh="x", auth="y")
    session.add(s1)
    await session.commit()

    s2 = PushSubscription(endpoint="https://example.com/1", p256dh="x", auth="y")
    session.add(s2)
    with pytest.raises(Exception):  # IntegrityError ou similar
        await session.commit()
```

- [ ] **Step 5.2: Run, fail, implement models**

Implementar `apps/api/src/scanner_api/db/models.py`:

```python
"""SQLAlchemy ORM models — espelha spec Section 7.3.

3 tabelas: jobs, job_files, push_subscriptions.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    """Base declarativa do scanner_api."""


JobStatus = Literal["queued", "running", "done", "error", "cancelled"]
FileRole = Literal["input", "output_md", "output_docx", "output_pdf", "image"]


class Job(Base):
    """Trabalho de OCR — agrupa N inputs e M outputs."""

    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String, primary_key=True)  # UUID4
    status: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    input_count: Mapped[int] = mapped_column(Integer, nullable=False)
    merge_mode: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    formats: Mapped[str] = mapped_column(String, nullable=False)
    advanced: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.current_timestamp()
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_favorite: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_msg: Mapped[str | None] = mapped_column(Text, nullable=True)
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    files: Mapped[list["JobFile"]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('queued','running','done','error','cancelled')",
            name="jobs_status_valid",
        ),
        Index("idx_jobs_expires_nonfav", "expires_at", sqlite_where=("is_favorite = 0")),
        Index("idx_jobs_created_desc", "created_at"),
    )


class JobFile(Base):
    """Arquivo associado a um Job (input ou output)."""

    __tablename__ = "job_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String, nullable=False)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)

    job: Mapped[Job] = relationship(back_populates="files")

    __table_args__ = (
        CheckConstraint(
            "role IN ('input','output_md','output_docx','output_pdf','image')",
            name="job_files_role_valid",
        ),
    )


class PushSubscription(Base):
    """Web Push subscription (browser/PWA)."""

    __tablename__ = "push_subscriptions"

    endpoint: Mapped[str] = mapped_column(String, primary_key=True)
    p256dh: Mapped[str] = mapped_column(String, nullable=False)
    auth: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.current_timestamp()
    )
    user_agent: Mapped[str | None] = mapped_column(String, nullable=True)
```

- [ ] **Step 5.3: Criar `apps/api/src/scanner_api/db/schema.sql` (referência humana — não executável)**

```sql
-- Schema canônico do scanner_api (espelha o ORM, ver db/models.py).
-- Mantido como referência humana e para debugging via sqlite3 CLI.
-- Migrações reais são geridas pelo Alembic.

CREATE TABLE jobs (
  id           TEXT PRIMARY KEY,
  status       TEXT NOT NULL CHECK(status IN ('queued','running','done','error','cancelled')),
  title        TEXT,
  input_count  INTEGER NOT NULL,
  merge_mode   INTEGER NOT NULL DEFAULT 0,
  formats      TEXT NOT NULL,
  advanced     TEXT,
  created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  finished_at  TIMESTAMP,
  expires_at   TIMESTAMP,
  is_favorite  INTEGER NOT NULL DEFAULT 0,
  error_msg    TEXT,
  page_count   INTEGER
);

CREATE TABLE job_files (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id      TEXT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
  role        TEXT NOT NULL CHECK(role IN ('input','output_md','output_docx','output_pdf','image')),
  filename    TEXT NOT NULL,
  size_bytes  INTEGER NOT NULL
);

CREATE TABLE push_subscriptions (
  endpoint    TEXT PRIMARY KEY,
  p256dh      TEXT NOT NULL,
  auth        TEXT NOT NULL,
  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  user_agent  TEXT
);

CREATE INDEX idx_jobs_expires_nonfav ON jobs(expires_at) WHERE is_favorite = 0;
CREATE INDEX idx_jobs_created_desc ON jobs(created_at DESC);
CREATE INDEX idx_job_files_job ON job_files(job_id);
```

- [ ] **Step 5.4: Criar Alembic infra**

Run:
```bash
cd apps/api
/c/Users/jacks/scoop/apps/python/current/python.exe -m alembic init -t async src/scanner_api/db/migrations
```

Editar `apps/api/alembic.ini`:
```ini
[alembic]
script_location = src/scanner_api/db/migrations
prepend_sys_path = .
sqlalchemy.url = sqlite+aiosqlite:///./scanner.db
file_template = %%(rev)s_%%(slug)s
```

Editar `apps/api/src/scanner_api/db/migrations/env.py` (Alembic gera template — importar Base):

No topo do arquivo, após os imports padrão:
```python
from scanner_api.db.models import Base
target_metadata = Base.metadata
```

E na função `run_migrations_online`/`run_async_migrations`, garantir que `target_metadata=target_metadata` está presente.

- [ ] **Step 5.5: Gerar primeira migração**

Run:
```bash
cd apps/api
/c/Users/jacks/scoop/apps/python/current/python.exe -m alembic revision --autogenerate -m "initial schema (jobs, job_files, push_subscriptions)"
```

Inspecionar o arquivo gerado em `src/scanner_api/db/migrations/versions/<rev>_initial_schema.py` — deve criar as 3 tabelas + índices. Renomear (ou já gerar) como `0001_initial.py`.

- [ ] **Step 5.6: Tests verde**

Run: `cd apps/api && pytest tests/test_db_models.py -v`
Expected: 3 PASS.

- [ ] **Step 5.7: Commit**

```bash
git add apps/api/src/scanner_api/db/ apps/api/alembic.ini apps/api/tests/test_db_models.py
git commit -m "feat(api): add ORM models + Alembic init + initial migration

- Job, JobFile, PushSubscription (espelha spec Section 7.3)
- CheckConstraints inline para enums (status, role)
- Cascade delete: deletar Job apaga JobFiles
- Indexes: expires_nonfav, created_desc, fk(job_id)
- schema.sql como referência humana (debugging via sqlite3 CLI)
- Alembic initial migration (autogenerate)
- 3 tests cobrindo insert, cascade, unique endpoint"
```

---

## Task 6: Health endpoint /api/health

**Files:**
- Create: `apps/api/src/scanner_api/routes/__init__.py`
- Create: `apps/api/src/scanner_api/routes/health.py`
- Create: `apps/api/tests/test_health.py`
- Modify: `apps/api/src/scanner_api/main.py` (mount router)

- [ ] **Step 6.1: Tests primeiro**

```python
# apps/api/tests/test_health.py
"""Testes do endpoint /api/health."""

from __future__ import annotations

from httpx import AsyncClient


async def test_health_returns_200(client: AsyncClient) -> None:
    """GET /api/health responde 200."""
    response = await client.get("/api/health")
    assert response.status_code == 200


async def test_health_payload_shape(client: AsyncClient) -> None:
    """Payload tem todos os campos especificados (Section 7.1)."""
    response = await client.get("/api/health")
    body = response.json()
    expected_keys = {
        "device",
        "gpu_name",
        "queue_depth",
        "workers_busy",
        "db_size_mb",
        "disk_free_gb",
        "version",
    }
    assert set(body.keys()) >= expected_keys


async def test_health_device_is_valid(client: AsyncClient) -> None:
    """device é cuda | cpu (não 'auto' — já resolvido)."""
    response = await client.get("/api/health")
    body = response.json()
    assert body["device"] in ("cuda", "cpu")


async def test_health_queue_zero_initially(client: AsyncClient) -> None:
    """Phase 1A não tem worker pool ainda — queue_depth = 0."""
    response = await client.get("/api/health")
    body = response.json()
    assert body["queue_depth"] == 0
    assert body["workers_busy"] == 0


async def test_health_version_matches_package(client: AsyncClient) -> None:
    """version é o __version__ do scanner_api."""
    from scanner_api import __version__

    response = await client.get("/api/health")
    body = response.json()
    assert body["version"] == __version__
```

- [ ] **Step 6.2: Run, fail, implement**

Implementar `apps/api/src/scanner_api/routes/__init__.py`:

```python
"""HTTP routes — agrupados por área."""

from scanner_api.routes.health import router as health_router

__all__ = ["health_router"]
```

Implementar `apps/api/src/scanner_api/routes/health.py`:

```python
"""GET /api/health — informa estado do servidor (device, queue, disk).

Phase 1A: queue_depth e workers_busy retornam 0 (sem worker pool ainda).
Phase 1B atualiza esses valores conectando ao ProcessPoolExecutor real.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel

from scanner_api import __version__
from scanner_api.settings import get_settings

router = APIRouter(prefix="/api", tags=["health"])


class HealthResponse(BaseModel):
    """Payload do /api/health (espelha spec Section 7.1)."""

    device: str  # cuda | cpu
    gpu_name: str | None
    queue_depth: int
    workers_busy: int
    db_size_mb: float
    disk_free_gb: float
    version: str


def _resolve_device() -> tuple[str, str | None]:
    """Detecta device atual (CUDA disponível? GPU name?)."""
    settings = get_settings()
    if settings.device == "cpu":
        return "cpu", None
    try:
        import torch

        if torch.cuda.is_available():
            return "cuda", torch.cuda.get_device_name(0)
    except ImportError:
        pass
    return "cpu", None


def _db_size_mb(db_path: Path) -> float:
    """Tamanho do arquivo SQLite em MB. 0 se não existe ainda."""
    if not db_path.exists():
        return 0.0
    return db_path.stat().st_size / (1024 * 1024)


def _disk_free_gb(data_dir: Path) -> float:
    """Espaço livre no filesystem do data_dir, em GB."""
    if not data_dir.exists():
        data_dir = data_dir.parent
    usage = shutil.disk_usage(data_dir)
    return usage.free / (1024**3)


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Retorna estado do servidor."""
    settings = get_settings()
    device, gpu_name = _resolve_device()

    return HealthResponse(
        device=device,
        gpu_name=gpu_name,
        queue_depth=0,  # Phase 1B conecta com pool real
        workers_busy=0,
        db_size_mb=round(_db_size_mb(settings.db_path), 2),
        disk_free_gb=round(_disk_free_gb(settings.data_dir), 2),
        version=__version__,
    )
```

- [ ] **Step 6.3: Modificar `apps/api/src/scanner_api/main.py` para montar o router**

Em `create_app()`, antes do `return app`, adicionar:

```python
    from scanner_api.routes import health_router
    app.include_router(health_router)
```

- [ ] **Step 6.4: Run tests — verde**

Run: `cd apps/api && pytest tests/test_health.py -v`
Expected: 5 PASS.

- [ ] **Step 6.5: Smoke test manual**

Run em terminal separado:
```bash
cd apps/api
SCANNER_DATA_DIR=/tmp/scanner-test \
SCANNER_VAPID_PUBLIC_KEY=stub \
SCANNER_VAPID_PRIVATE_KEY=stub \
SCANNER_VAPID_EMAIL=t@e.com \
/c/Users/jacks/scoop/apps/python/current/python.exe -m uvicorn scanner_api.main:app --port 8000
```

Em outro terminal: `curl http://localhost:8000/api/health` (ou via browser).

Expected: JSON com 7 campos preenchidos. Device deve ser `cuda` se você tem GPU local, senão `cpu`.

- [ ] **Step 6.6: Run all api tests + ruff**

Run:
```bash
cd apps/api
pytest tests/ -v
/c/Users/jacks/scoop/apps/python/current/python.exe -m ruff check src/scanner_api/ tests/
```

Expected: 18+ tests pass, ruff clean.

- [ ] **Step 6.7: Commit**

```bash
git add apps/api/src/scanner_api/routes/ apps/api/src/scanner_api/main.py apps/api/tests/test_health.py
git commit -m "feat(api): add GET /api/health endpoint

- HealthResponse model: device, gpu_name, queue_depth, workers_busy,
  db_size_mb, disk_free_gb, version (matches spec Section 7.1)
- _resolve_device() consulta torch.cuda.is_available()
- _db_size_mb / _disk_free_gb usam shutil + stat
- queue_depth/workers_busy retornam 0 (Phase 1B vai conectar com pool real)
- Router montado em main.py via include_router
- 5 testes E2E via httpx ASGI client

Phase 1A complete — backend roda standalone com /api/health.
Plan: docs/superpowers/plans/2026-05-02-phase-1a-fastapi-foundation.md (Task 6/6)"
```

---

## Self-Review

**1. Spec coverage (Phase 1A subset):**
- ✅ Estrutura `apps/api/` (Section 6) — Tasks 1, 2
- ✅ Settings env vars (Section 7.5) — Task 2
- ✅ Storage layout (Section 6 + 7) — Task 3
- ✅ DB engine + models (Section 7.3) — Tasks 4, 5
- ✅ /api/health (Section 7.1, primeiro endpoint) — Task 6
- ⏭️ Demais endpoints (POST jobs, WebSocket, push) → Phase 1B/1C

**2. Placeholder scan:** ✅ Sem TODO/TBD. Cada step tem código completo.

**3. Type consistency:**
- ✅ `Settings.data_dir: Path`, `db_path: Path` — consistente
- ✅ `Job.status: str` com CheckConstraint — consistente com Literal type
- ✅ `HealthResponse` matches spec exatamente
- ✅ `get_session()` cede `AsyncSession` — usado por endpoints futuros

**4. Risk areas:**
- Alembic init em `Path` com Unicode (`²º Cérebro`) pode dar problemas. Plano: gerar localmente, mas no Dockerfile o path é `/app/apps/api` (Linux puro). Mitigação no Step 5.4.
- Pydantic Settings v2 é estrito — `extra="ignore"` para tolerar env vars não-relacionadas.
- SQLAlchemy 2.0 + aiosqlite: SQLite tem limitações de concorrência (1 writer). Aceitável para single-tenant.

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-05-02-phase-1a-fastapi-foundation.md`. Two execution options:**

**1. Subagent-Driven (Phase 0 mostrou que subagents podem thrashar contra o CLAUDE.md/MCP do repo)** — para Phase 1A o escopo é `apps/api/` (fora do CLAUDE.md root rules influence) então pode funcionar melhor.

**2. Inline Execution (preferida pela experiência da Phase 0)** — execução direta nesta sessão, com checkpoints por task.

**Próximo plano: Phase 1B** (worker pool + jobs CRUD + WebSocket progress) — gerado após Phase 1A completar.
**Phase 1C** (push notifications + purge cron) — gerado após Phase 1B completar.
