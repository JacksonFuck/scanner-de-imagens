"""Pub/sub assíncrono de eventos de progresso de job.

Cada job_id tem um asyncio.Event compartilhado: workers (ou file tail)
fazem `signal()`, consumidores WebSocket fazem `wait()`. Eventos são lidos
do disco (`<job>/.progress.jsonl`, append-only).

Como a escrita acontece em outro processo (subprocess do worker), o canal
de coordenação é o próprio arquivo. O Event aqui é só um "spotlight" para
acordar o tail loop — caso contrário ele dormiria com `await sleep()`.
"""

from __future__ import annotations

import asyncio
import json
from collections import defaultdict
from collections.abc import AsyncIterator
from pathlib import Path

import aiofiles


class ProgressBroker:
    """Distribui eventos do .progress.jsonl para clientes WebSocket."""

    def __init__(self) -> None:
        self._events: dict[str, asyncio.Event] = defaultdict(asyncio.Event)

    def signal(self, job_id: str) -> None:
        """Sinaliza que novos eventos foram escritos no .progress.jsonl.

        Como o arquivo é escrito por outro processo (worker subprocess),
        este `signal()` é tipicamente chamado pela API que sabe quando
        novos eventos vieram (por agora, tail loop com sleep curto descobre
        sozinho — método mantido para futuras integrações).
        """
        evt = self._events.get(job_id)
        if evt is not None:
            evt.set()
            self._events[job_id] = asyncio.Event()  # rearm

    async def stream(
        self,
        job_id: str,
        progress_path: Path,
        *,
        poll_interval: float = 0.1,
        wait_for_file_timeout: float = 30.0,
    ) -> AsyncIterator[dict]:
        """Yields cada nova linha do .progress.jsonl como dict.

        Termina quando aparece um evento {type: 'done'|'error'|'cancelled'}
        OU quando o cliente fecha a conexão (cancelamento da task).

        Args:
            job_id: Identificador do job (usado para logging e Event).
            progress_path: Path do .progress.jsonl.
            poll_interval: Tempo entre tentativas de leitura quando EOF.
            wait_for_file_timeout: Tempo máximo aguardando o arquivo aparecer.
        """
        # Espera arquivo existir (worker pode ainda não ter escrito a 1ª linha)
        elapsed = 0.0
        while not progress_path.exists():
            if elapsed >= wait_for_file_timeout:
                yield {"type": "error", "message": "progress file timeout"}
                return
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        async with aiofiles.open(progress_path) as f:
            while True:
                line = await f.readline()
                if line:
                    stripped = line.strip()
                    if not stripped:
                        continue
                    try:
                        event = json.loads(stripped)
                    except json.JSONDecodeError:
                        continue
                    yield event
                    if event.get("type") in ("done", "error", "cancelled"):
                        return
                else:
                    # EOF — espera novo evento
                    await asyncio.sleep(poll_interval)


# Singleton global do broker
_broker = ProgressBroker()


def get_broker() -> ProgressBroker:
    """Retorna a instância singleton do ProgressBroker."""
    return _broker
