"""WebSocket /ws/jobs/{job_id} — streaming de eventos de progresso.

Cliente conecta e recebe um JSON por evento ('started', 'progress',
'done', 'error', 'cancelled'). O socket fecha quando aparece um evento
terminal (done/error/cancelled).

Os eventos vêm do `<job>/.progress.jsonl` (escrito pelo worker subprocess).
Usamos `ProgressBroker.stream()` que faz tail assíncrono do arquivo.
"""

from __future__ import annotations

import contextlib
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from scanner_api.progress import get_broker
from scanner_api.settings import get_settings
from scanner_api.storage import job_progress_path

log = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["ws"])


@router.websocket("/jobs/{job_id}")
async def job_progress_ws(websocket: WebSocket, job_id: str) -> None:
    """Stream eventos do .progress.jsonl como JSON ao cliente.

    Args:
        websocket: Conexão FastAPI.
        job_id: Identificador do job. Não validamos no DB — broker apenas
            faz tail do arquivo `.progress.jsonl`. Se job não existir,
            stream emite type='error' por timeout (configurável).
    """
    await websocket.accept()
    settings = get_settings()
    progress_path = job_progress_path(settings.data_dir, job_id)
    broker = get_broker()

    try:
        async for event in broker.stream(job_id, progress_path):
            await websocket.send_json(event)
    except WebSocketDisconnect:
        log.debug("WS disconnected for job %s", job_id)
        return
    finally:
        # close() é idempotente; tenta encerrar gracefully
        with contextlib.suppress(RuntimeError):
            # Já fechado pelo client → suprime
            await websocket.close()
