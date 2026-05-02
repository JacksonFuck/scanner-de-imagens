"""Testes dos endpoints de push subscriptions e do wrapper push.send_push.

Mocks: pywebpush.webpush é stubado para não fazer requests reais.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from httpx import AsyncClient


async def test_vapid_public_key_returned(client: AsyncClient) -> None:
    """GET /api/push/vapid-public-key retorna a chave do settings."""
    response = await client.get("/api/push/vapid-public-key")
    assert response.status_code == 200
    body = response.json()
    assert body == {"public_key": "test-public-key"}


async def test_subscribe_persists(client: AsyncClient, tmp_data_dir: Path) -> None:
    """POST /api/push/subscribe grava PushSubscription no DB."""
    payload = {
        "endpoint": "https://push.example.com/abc",
        "keys": {"p256dh": "pubkey123", "auth": "auth123"},
        "user_agent": "Mozilla/5.0",
    }
    response = await client.post("/api/push/subscribe", json=payload)
    assert response.status_code == 201
    assert response.json() == {"ok": True}

    from scanner_api.db.engine import async_session_factory
    from scanner_api.db.models import PushSubscription

    factory = async_session_factory()
    async with factory() as session:
        sub = await session.get(PushSubscription, "https://push.example.com/abc")
        assert sub is not None
        assert sub.p256dh == "pubkey123"
        assert sub.auth == "auth123"
        assert sub.user_agent == "Mozilla/5.0"


async def test_subscribe_upsert(client: AsyncClient, tmp_data_dir: Path) -> None:
    """Subscribe duas vezes com mesmo endpoint atualiza as keys (upsert)."""
    endpoint = "https://push.example.com/dup"
    body1 = {
        "endpoint": endpoint,
        "keys": {"p256dh": "k1", "auth": "a1"},
    }
    body2 = {
        "endpoint": endpoint,
        "keys": {"p256dh": "k2", "auth": "a2"},
    }
    r1 = await client.post("/api/push/subscribe", json=body1)
    r2 = await client.post("/api/push/subscribe", json=body2)
    assert r1.status_code == 201
    assert r2.status_code == 201

    from scanner_api.db.engine import async_session_factory
    from scanner_api.db.models import PushSubscription

    factory = async_session_factory()
    async with factory() as session:
        sub = await session.get(PushSubscription, endpoint)
        assert sub is not None
        assert sub.p256dh == "k2"
        assert sub.auth == "a2"


async def test_unsubscribe_deletes(client: AsyncClient, tmp_data_dir: Path) -> None:
    """DELETE /api/push/unsubscribe remove a row."""
    endpoint = "https://push.example.com/del"
    await client.post(
        "/api/push/subscribe",
        json={"endpoint": endpoint, "keys": {"p256dh": "p", "auth": "a"}},
    )

    response = await client.request(
        "DELETE", "/api/push/unsubscribe", json={"endpoint": endpoint}
    )
    assert response.status_code == 200

    from scanner_api.db.engine import async_session_factory
    from scanner_api.db.models import PushSubscription

    factory = async_session_factory()
    async with factory() as session:
        sub = await session.get(PushSubscription, endpoint)
        assert sub is None


async def test_unsubscribe_idempotent(
    client: AsyncClient, tmp_data_dir: Path
) -> None:
    """DELETE de endpoint inexistente retorna 200 ok (idempotente)."""
    response = await client.request(
        "DELETE",
        "/api/push/unsubscribe",
        json={"endpoint": "https://push.example.com/missing"},
    )
    assert response.status_code == 200


def test_send_push_returns_success_on_2xx(tmp_data_dir: Path) -> None:
    """send_push retorna PushResult(success=True, expired=False) em 2xx."""
    from scanner_api.push import send_push

    with patch("scanner_api.push.webpush") as mock_wp:
        mock_wp.return_value = None  # webpush retorna None em sucesso
        result = send_push(
            "https://push.example.com/x",
            "p256",
            "auth",
            {"title": "Hi", "body": "ok"},
        )
    assert result.success is True
    assert result.expired is False


def test_send_push_marks_expired_on_410(tmp_data_dir: Path) -> None:
    """410 Gone → expired=True para que caller delete a sub."""
    from pywebpush import WebPushException

    from scanner_api.push import send_push

    class _Resp:
        status_code = 410
        text = "gone"

    err = WebPushException("expired", response=_Resp())

    with patch("scanner_api.push.webpush", side_effect=err):
        result = send_push(
            "https://push.example.com/x",
            "p256",
            "auth",
            {"title": "Hi"},
        )
    assert result.success is False
    assert result.expired is True


def test_send_push_other_error_not_expired(tmp_data_dir: Path) -> None:
    """500 do push service: success=False mas expired=False (não deletar)."""
    from pywebpush import WebPushException

    from scanner_api.push import send_push

    class _Resp:
        status_code = 500
        text = "boom"

    err = WebPushException("boom", response=_Resp())

    with patch("scanner_api.push.webpush", side_effect=err):
        result = send_push(
            "https://push.example.com/x",
            "p256",
            "auth",
            {"title": "Hi"},
        )
    assert result.success is False
    assert result.expired is False


@pytest.mark.asyncio
async def test_finalize_job_dispatches_push_when_done(
    client: AsyncClient, tmp_data_dir: Path
) -> None:
    """Quando _finalize_job vê status=done, chama send_push para cada sub."""
    # Cria 1 job no DB + 1 subscription
    from scanner_api.db.engine import async_session_factory
    from scanner_api.db.models import Job, PushSubscription
    from scanner_api.workers.pool import _finalize_job

    factory = async_session_factory()
    async with factory() as session:
        job = Job(
            id="job-test-1",
            status="running",
            title="Test",
            input_count=1,
            formats="md",
        )
        sub = PushSubscription(
            endpoint="https://push.example.com/finalize",
            p256dh="p",
            auth="a",
        )
        session.add(job)
        session.add(sub)
        await session.commit()

    with patch("scanner_api.workers.pool.send_push") as mock_send:
        from scanner_api.push import PushResult

        mock_send.return_value = PushResult(success=True, expired=False)
        await _finalize_job(
            "job-test-1",
            {"status": "done", "page_count": 5, "output_files": ["a.md"]},
        )

    # Verifica push foi chamado
    assert mock_send.call_count == 1
    args = mock_send.call_args
    assert args.args[0] == "https://push.example.com/finalize"
    payload = args.args[3]
    assert "title" in payload
    assert payload["url"] == "/jobs/job-test-1"

    # Verifica que job foi atualizado para status=done
    async with factory() as session:
        job_after = await session.get(Job, "job-test-1")
        assert job_after is not None
        assert job_after.status == "done"
        assert job_after.page_count == 5
        assert job_after.finished_at is not None


@pytest.mark.asyncio
async def test_finalize_job_removes_expired_subs(
    client: AsyncClient, tmp_data_dir: Path
) -> None:
    """Subscription que retorna 410 é deletada do DB após _finalize_job."""
    from scanner_api.db.engine import async_session_factory
    from scanner_api.db.models import Job, PushSubscription
    from scanner_api.workers.pool import _finalize_job

    factory = async_session_factory()
    async with factory() as session:
        session.add(
            Job(
                id="job-test-2",
                status="running",
                title="X",
                input_count=1,
                formats="md",
            )
        )
        session.add(
            PushSubscription(
                endpoint="https://push.example.com/exp",
                p256dh="p",
                auth="a",
            )
        )
        await session.commit()

    with patch("scanner_api.workers.pool.send_push") as mock_send:
        from scanner_api.push import PushResult

        mock_send.return_value = PushResult(success=False, expired=True)
        await _finalize_job(
            "job-test-2",
            {"status": "done", "page_count": 1, "output_files": []},
        )

    async with factory() as session:
        sub = await session.get(
            PushSubscription, "https://push.example.com/exp"
        )
        assert sub is None
