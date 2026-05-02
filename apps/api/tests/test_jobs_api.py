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


# ---------------------------------------------------------------------------
# GET /api/jobs (list + detail)
# ---------------------------------------------------------------------------


async def test_list_jobs_empty_returns_empty_array(client: AsyncClient) -> None:
    """Sem jobs no DB, GET /api/jobs retorna []."""
    response = await client.get("/api/jobs")
    assert response.status_code == 200
    assert response.json() == []


async def test_list_jobs_after_create_includes_new_job(
    client: AsyncClient,
) -> None:
    """Cria 1 job e confirma que aparece na listagem."""
    files = {"files": ("test.jpg", b"x", "image/jpeg")}
    create = await client.post("/api/jobs", files=files, data={"formats": "md"})
    job_id = create.json()["job_id"]

    listing = await client.get("/api/jobs")
    assert listing.status_code == 200
    body = listing.json()
    assert len(body) == 1
    assert body[0]["id"] == job_id
    assert body[0]["status"] == "queued"
    # Schema sanity: tem campos de JobSummary
    assert {"id", "status", "title", "input_count", "formats", "created_at", "is_favorite"} <= set(
        body[0].keys()
    )


async def test_list_jobs_filters_by_favorite(client: AsyncClient) -> None:
    """?favorite=1 só retorna jobs favoritos. Sem nenhum favorito → []."""
    files = {"files": ("test.jpg", b"x", "image/jpeg")}
    await client.post("/api/jobs", files=files, data={"formats": "md"})

    fav = await client.get("/api/jobs?favorite=1")
    assert fav.status_code == 200
    assert fav.json() == []  # nenhum criado como favorito

    nofav = await client.get("/api/jobs?favorite=0")
    assert nofav.status_code == 200
    assert len(nofav.json()) == 1


async def test_list_jobs_rejects_invalid_status(client: AsyncClient) -> None:
    """status fora dos válidos → 400."""
    response = await client.get("/api/jobs?status=bogus")
    assert response.status_code == 400


async def test_list_jobs_orders_by_created_desc(client: AsyncClient) -> None:
    """Jobs mais recentes vêm primeiro."""
    # Cria 3 jobs em sequência
    job_ids = []
    for i in range(3):
        files = {"files": (f"f{i}.jpg", b"x", "image/jpeg")}
        r = await client.post("/api/jobs", files=files, data={"formats": "md"})
        job_ids.append(r.json()["job_id"])

    listing = await client.get("/api/jobs")
    body = listing.json()
    assert len(body) == 3
    # Mais recente primeiro = job_ids[-1] no topo
    assert body[0]["id"] == job_ids[-1]
    assert body[-1]["id"] == job_ids[0]


async def test_get_job_detail_includes_files(client: AsyncClient) -> None:
    """GET /api/jobs/{id} retorna detalhe + files."""
    files = {"files": ("foto.jpg", b"x", "image/jpeg")}
    create = await client.post(
        "/api/jobs", files=files, data={"formats": "all", "title": "X"}
    )
    job_id = create.json()["job_id"]

    detail = await client.get(f"/api/jobs/{job_id}")
    assert detail.status_code == 200
    body = detail.json()
    assert body["id"] == job_id
    assert body["title"] == "X"
    assert body["formats"] == "all"
    assert len(body["files"]) == 1
    assert body["files"][0]["role"] == "input"
    assert body["files"][0]["filename"] == "foto.jpg"


async def test_get_job_404_for_nonexistent(client: AsyncClient) -> None:
    """ID inexistente → 404."""
    response = await client.get("/api/jobs/nonexistent-id")
    assert response.status_code == 404
    assert "não encontrado" in response.json()["detail"].lower()
