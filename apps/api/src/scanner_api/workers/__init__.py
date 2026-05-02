"""Worker pool + subprocess entry point.

`pool.WorkerPool` gerencia o ProcessPoolExecutor.
`worker_main.process_job` é chamado dentro de cada subprocess.
"""

from __future__ import annotations

from scanner_api.workers.pool import (
    WorkerPool,
    get_pool,
    init_pool,
    shutdown_pool,
)
from scanner_api.workers.worker_main import WorkerJobSpec, WorkerResult, process_job

__all__ = [
    "WorkerJobSpec",
    "WorkerPool",
    "WorkerResult",
    "get_pool",
    "init_pool",
    "process_job",
    "shutdown_pool",
]
