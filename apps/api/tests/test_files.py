"""Testes do GET /api/jobs/{job_id}/files/{filename}.

Inclui validação de:
- 404 quando job não existe
- 404 quando arquivo não existe
- Download bem-sucedido com Content-Disposition correto
- Procura em outputs/, images/, inputs/ (ordem de prioridade)
- Proteção contra path traversal (../etc/passwd)
"""

from __future__ import annotations

from pathlib import Path

from httpx import AsyncClient


async def test_download_404_for_nonexistent_job(client: AsyncClient) -> None:
    """Job que não existe → 404 (mesmo com filename arbitrário)."""
    response = await client.get("/api/jobs/none-existent/files/x.md")
    assert response.status_code == 404
    assert "não encontrado" in response.json()["detail"].lower()


async def test_download_404_for_nonexistent_file(
    client: AsyncClient, tmp_data_dir: Path
) -> None:
    """Job existe mas arquivo não → 404."""
    # Cria job
    files = {"files": ("foto.jpg", b"x", "image/jpeg")}
    create = await client.post("/api/jobs", files=files, data={"formats": "md"})
    job_id = create.json()["job_id"]

    # Pede arquivo que não existe
    response = await client.get(f"/api/jobs/{job_id}/files/nonexistent.md")
    assert response.status_code == 404


async def test_download_returns_input_file(
    client: AsyncClient, tmp_data_dir: Path
) -> None:
    """Arquivo de input enviado pode ser baixado de volta."""
    payload = b"\xff\xd8\xff\xe0meu-jpg-bytes"
    files = {"files": ("foto.jpg", payload, "image/jpeg")}
    create = await client.post("/api/jobs", files=files, data={"formats": "md"})
    job_id = create.json()["job_id"]

    response = await client.get(f"/api/jobs/{job_id}/files/foto.jpg")
    assert response.status_code == 200
    assert response.content == payload
    # Content-Disposition: attachment
    cd = response.headers.get("content-disposition", "").lower()
    assert "attachment" in cd
    assert "foto.jpg" in cd


async def test_download_finds_output_md(
    client: AsyncClient, tmp_data_dir: Path
) -> None:
    """Arquivo em outputs/ é encontrado e servido (prioritário sobre inputs)."""
    files = {"files": ("foto.jpg", b"x", "image/jpeg")}
    create = await client.post("/api/jobs", files=files, data={"formats": "md"})
    job_id = create.json()["job_id"]

    # Simula que o worker gerou foto.md em outputs/
    output_md = tmp_data_dir / "jobs" / job_id / "outputs" / "foto.md"
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("# Hello\n\nConteudo extraido.\n", encoding="utf-8")

    response = await client.get(f"/api/jobs/{job_id}/files/foto.md")
    assert response.status_code == 200
    assert b"Hello" in response.content


async def test_download_blocks_path_traversal(
    client: AsyncClient, tmp_data_dir: Path
) -> None:
    """`..%2Fetc%2Fpasswd` ou similar deve ser rejeitado.

    FastAPI/Starlette normaliza alguns padrões — o teste valida que
    nenhum filename contendo '..' resulta em servir arquivo fora do
    job_dir.
    """
    files = {"files": ("foto.jpg", b"x", "image/jpeg")}
    create = await client.post("/api/jobs", files=files, data={"formats": "md"})
    job_id = create.json()["job_id"]

    # Tenta traversal via URL encoded
    response = await client.get(
        f"/api/jobs/{job_id}/files/..%2F..%2Fscanner.db"
    )
    # Aceitável: 400 (path inválido), 404 (não achou nada legítimo) ou
    # 405 (Starlette redirecionou). O que NÃO pode é 200 retornando o DB.
    assert response.status_code in (400, 404, 405)
    if response.status_code == 200:
        # Se chegou 200 (não deveria), confirma que não vazou o DB
        assert b"SQLite" not in response.content


async def test_download_priority_outputs_over_inputs(
    client: AsyncClient, tmp_data_dir: Path
) -> None:
    """Se mesmo nome em outputs/ e inputs/, outputs/ ganha (mais novo)."""
    files = {"files": ("doc.md", b"INPUT-version", "text/markdown")}
    create = await client.post("/api/jobs", files=files, data={"formats": "md"})
    job_id = create.json()["job_id"]

    # Simula output com mesmo nome
    output_md = tmp_data_dir / "jobs" / job_id / "outputs" / "doc.md"
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("OUTPUT-version", encoding="utf-8")

    response = await client.get(f"/api/jobs/{job_id}/files/doc.md")
    assert response.status_code == 200
    assert response.content == b"OUTPUT-version"
