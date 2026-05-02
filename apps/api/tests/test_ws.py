"""Testes do WebSocket /ws/jobs/{job_id}.

Usa starlette TestClient (síncrono) porque httpx async não suporta WS.
Injetamos eventos manualmente no .progress.jsonl para validar o stream
sem precisar rodar Docling de verdade.
"""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from scanner_api.storage import ensure_job_dirs, job_progress_path


def test_ws_streams_events_from_progress_file(
    app, tmp_data_dir: Path
) -> None:
    """Escreve eventos no .progress.jsonl e valida que chegam ao WS."""
    job_id = "test-ws-stream"
    ensure_job_dirs(tmp_data_dir, job_id)
    progress_path = job_progress_path(tmp_data_dir, job_id)
    progress_path.write_text(
        json.dumps({"type": "started", "input_count": 1}) + "\n"
        + json.dumps({"type": "progress", "current": 1, "total": 1}) + "\n"
        + json.dumps({"type": "done", "page_count": 1}) + "\n",
        encoding="utf-8",
    )

    with TestClient(app) as tc, tc.websocket_connect(f"/ws/jobs/{job_id}") as ws:
        evt1 = ws.receive_json()
        evt2 = ws.receive_json()
        evt3 = ws.receive_json()

    assert evt1["type"] == "started"
    assert evt1["input_count"] == 1
    assert evt2["type"] == "progress"
    assert evt2["current"] == 1
    assert evt3["type"] == "done"


def test_ws_terminates_on_error_event(app, tmp_data_dir: Path) -> None:
    """Evento type=error encerra o stream."""
    job_id = "test-ws-error"
    ensure_job_dirs(tmp_data_dir, job_id)
    progress_path = job_progress_path(tmp_data_dir, job_id)
    progress_path.write_text(
        json.dumps({"type": "started"}) + "\n"
        + json.dumps({"type": "error", "message": "boom"}) + "\n",
        encoding="utf-8",
    )

    with TestClient(app) as tc, tc.websocket_connect(f"/ws/jobs/{job_id}") as ws:
        ws.receive_json()  # started
        err = ws.receive_json()  # error

    assert err["type"] == "error"
    assert err["message"] == "boom"


def test_ws_emits_timeout_error_for_nonexistent_job(
    app, tmp_data_dir: Path, monkeypatch
) -> None:
    """Job sem .progress.jsonl criado → broker emite type=error após timeout.

    Tornamos o timeout curto (200ms) para o teste rodar rápido.
    """
    # Reduz timeout do broker para o teste
    from scanner_api.progress import get_broker

    original_stream = get_broker().stream

    async def short_stream(job_id, progress_path, **kwargs):
        kwargs.setdefault("poll_interval", 0.05)
        kwargs.setdefault("wait_for_file_timeout", 0.2)
        async for ev in original_stream(job_id, progress_path, **kwargs):
            yield ev

    monkeypatch.setattr(get_broker(), "stream", short_stream)

    with TestClient(app) as tc, tc.websocket_connect("/ws/jobs/never-exists") as ws:
        evt = ws.receive_json()

    assert evt["type"] == "error"
    assert "timeout" in evt["message"].lower()
