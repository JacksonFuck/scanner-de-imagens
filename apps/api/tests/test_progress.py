"""Testes do ProgressBroker — pub/sub via .progress.jsonl."""

from __future__ import annotations

import json
from pathlib import Path

from scanner_api.progress import ProgressBroker, get_broker


async def test_progress_stream_yields_events_until_done(tmp_path: Path) -> None:
    """stream() yields cada linha JSON e termina em type=done."""
    progress_path = tmp_path / "progress.jsonl"
    progress_path.write_text(
        json.dumps({"type": "started"}) + "\n"
        + json.dumps({"type": "progress", "current": 1, "total": 2}) + "\n"
        + json.dumps({"type": "done"}) + "\n",
        encoding="utf-8",
    )

    broker = ProgressBroker()
    events: list[dict] = []
    async for evt in broker.stream("job-x", progress_path):
        events.append(evt)
    assert [e["type"] for e in events] == ["started", "progress", "done"]


async def test_progress_stream_terminates_on_error(tmp_path: Path) -> None:
    """type=error também encerra o stream."""
    progress_path = tmp_path / "progress.jsonl"
    progress_path.write_text(
        json.dumps({"type": "started"}) + "\n"
        + json.dumps({"type": "error", "message": "boom"}) + "\n",
        encoding="utf-8",
    )

    broker = ProgressBroker()
    events = []
    async for evt in broker.stream("job-y", progress_path):
        events.append(evt)
    assert events[-1]["type"] == "error"
    assert events[-1]["message"] == "boom"


async def test_progress_stream_skips_invalid_json(tmp_path: Path) -> None:
    """Linhas malformadas são ignoradas (não derrubam o stream)."""
    progress_path = tmp_path / "progress.jsonl"
    progress_path.write_text(
        json.dumps({"type": "started"}) + "\n"
        + "not-valid-json\n"
        + json.dumps({"type": "done"}) + "\n",
        encoding="utf-8",
    )

    broker = ProgressBroker()
    events = []
    async for evt in broker.stream("job-z", progress_path):
        events.append(evt)
    # 2 eventos válidos, ignora a linha inválida
    assert len(events) == 2


async def test_progress_stream_timeouts_when_file_never_appears(
    tmp_path: Path,
) -> None:
    """Se o arquivo nunca aparecer, stream emite erro e encerra."""
    progress_path = tmp_path / "never-created.jsonl"
    broker = ProgressBroker()
    events = []
    async for evt in broker.stream(
        "job-t", progress_path, poll_interval=0.05, wait_for_file_timeout=0.2
    ):
        events.append(evt)
    assert len(events) == 1
    assert events[0]["type"] == "error"
    assert "timeout" in events[0]["message"].lower()


def test_get_broker_returns_singleton() -> None:
    """get_broker() retorna sempre a mesma instância."""
    b1 = get_broker()
    b2 = get_broker()
    assert b1 is b2
