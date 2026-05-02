"""Testes do POST /api/jobs.

Pool não está ativo nestes testes (lifespan não roda em httpx ASGI),
então o handler tem fallback que loga warning e segue. Validamos:
- 201 Created com job_id e status='queued'
- Job e JobFile gravados no DB
- Inputs salvos em /data/jobs/{id}/inputs/
- Validação de formato e arquivos
"""

from __future__ import annotations

from pathlib import Path

from httpx import AsyncClient


async def test_create_job_returns_201_with_job_id(
    client: AsyncClient, tmp_data_dir: Path
) -> None:
    """POST básico: 1 arquivo, formato 'md'."""
    files = {"files": ("test.jpg", b"fake-jpg-bytes", "image/jpeg")}
    response = await client.post("/api/jobs", files=files, data={"formats": "md"})
    assert response.status_code == 201
    body = response.json()
    assert "job_id" in body
    assert body["status"] == "queued"
    # UUID4 tem 36 chars
    assert len(body["job_id"]) == 36


async def test_create_job_persists_input_to_disk(
    client: AsyncClient, tmp_data_dir: Path
) -> None:
    """Arquivo subido fica em /data/jobs/{job_id}/inputs/."""
    payload = b"\xff\xd8\xff\xe0fake-jpg"
    files = {"files": ("foto.jpg", payload, "image/jpeg")}
    response = await client.post("/api/jobs", files=files, data={"formats": "md"})
    job_id = response.json()["job_id"]
    saved = tmp_data_dir / "jobs" / job_id / "inputs" / "foto.jpg"
    assert saved.exists()
    assert saved.read_bytes() == payload


async def test_create_job_persists_to_db(
    client: AsyncClient, tmp_data_dir: Path
) -> None:
    """Job + JobFile gravados no DB."""
    files = {"files": ("foto.jpg", b"x", "image/jpeg")}
    response = await client.post(
        "/api/jobs", files=files, data={"formats": "pdf", "title": "Teste"}
    )
    job_id = response.json()["job_id"]


    from scanner_api.db.engine import async_session_factory
    from scanner_api.db.models import Job

    factory = async_session_factory()
    async with factory() as session:
        job = await session.get(Job, job_id)
        assert job is not None
        assert job.status == "queued"
        assert job.title == "Teste"
        assert job.formats == "pdf"
        assert job.input_count == 1
        # Eager load files
        await session.refresh(job, ["files"])
        assert len(job.files) == 1
        assert job.files[0].role == "input"
        assert job.files[0].filename == "foto.jpg"


async def test_create_job_with_multiple_files(
    client: AsyncClient, tmp_data_dir: Path
) -> None:
    """Multipart com vários arquivos cria 1 Job + N JobFile inputs."""
    files = [
        ("files", ("a.jpg", b"a", "image/jpeg")),
        ("files", ("b.jpg", b"b", "image/jpeg")),
        ("files", ("c.jpg", b"c", "image/jpeg")),
    ]
    response = await client.post(
        "/api/jobs", files=files, data={"formats": "all", "merge": "true"}
    )
    assert response.status_code == 201
    job_id = response.json()["job_id"]

    # Os 3 inputs no disco
    inputs_dir = tmp_data_dir / "jobs" / job_id / "inputs"
    assert {p.name for p in inputs_dir.iterdir()} == {"a.jpg", "b.jpg", "c.jpg"}


async def test_create_job_rejects_invalid_format(client: AsyncClient) -> None:
    """Formato fora de md|docx|pdf|all|both → 400."""
    files = {"files": ("test.jpg", b"x", "image/jpeg")}
    response = await client.post(
        "/api/jobs", files=files, data={"formats": "bogus"}
    )
    assert response.status_code == 400
    assert "inválido" in response.json()["detail"].lower()


async def test_create_job_rejects_no_files(client: AsyncClient) -> None:
    """POST sem arquivos retorna 422 (FastAPI validation)."""
    response = await client.post("/api/jobs", data={"formats": "md"})
    # FastAPI retorna 422 quando o campo obrigatório `files` falta
    assert response.status_code in (400, 422)


async def test_create_job_advanced_options_persisted(
    client: AsyncClient, tmp_data_dir: Path
) -> None:
    """Advanced é JSON-encoded e fica em job.advanced."""
    advanced_json = (
        '{"do_ocr": false, "do_tables": true, "ocr_engine": "tesseract", '
        '"ocr_lang": "pt", "device": "cpu"}'
    )
    files = {"files": ("test.jpg", b"x", "image/jpeg")}
    response = await client.post(
        "/api/jobs",
        files=files,
        data={"formats": "md", "advanced": advanced_json},
    )
    assert response.status_code == 201
    job_id = response.json()["job_id"]

    from scanner_api.db.engine import async_session_factory
    from scanner_api.db.models import Job

    factory = async_session_factory()
    async with factory() as session:
        job = await session.get(Job, job_id)
        assert job is not None
        # advanced é JSON-encoded
        assert job.advanced is not None
        assert "tesseract" in job.advanced


async def test_create_job_rejects_malformed_advanced(client: AsyncClient) -> None:
    """Advanced JSON malformado retorna 400."""
    files = {"files": ("test.jpg", b"x", "image/jpeg")}
    response = await client.post(
        "/api/jobs",
        files=files,
        data={"formats": "md", "advanced": "{invalid json"},
    )
    assert response.status_code == 400
