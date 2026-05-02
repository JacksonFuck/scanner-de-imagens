"""Web Push subscription endpoints.

- GET /api/push/vapid-public-key → cliente baixa para registrar SW
- POST /api/push/subscribe → grava PushSubscription no DB (upsert)
- DELETE /api/push/unsubscribe → remove por endpoint
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from scanner_api.db import get_session
from scanner_api.db.models import PushSubscription
from scanner_api.settings import get_settings

log = logging.getLogger(__name__)

router = APIRouter(prefix="/api/push", tags=["push"])


class VapidPublicKeyResponse(BaseModel):
    public_key: str


class PushKeys(BaseModel):
    p256dh: str
    auth: str


class SubscribeRequest(BaseModel):
    endpoint: str
    keys: PushKeys
    user_agent: str | None = None


class UnsubscribeRequest(BaseModel):
    endpoint: str


class SubscribeResponse(BaseModel):
    ok: bool


@router.get("/vapid-public-key", response_model=VapidPublicKeyResponse)
async def vapid_public_key() -> VapidPublicKeyResponse:
    """Retorna a chave pública VAPID (base64url) para o frontend usar
    em `pushManager.subscribe({applicationServerKey})`.
    """
    settings = get_settings()
    return VapidPublicKeyResponse(public_key=settings.vapid_public_key)


@router.post("/subscribe", response_model=SubscribeResponse, status_code=201)
async def subscribe(
    body: SubscribeRequest,
    session: AsyncSession = Depends(get_session),
) -> SubscribeResponse:
    """Registra (upsert) uma subscription no DB.

    Endpoint é PRIMARY KEY — re-subscribe do mesmo device atualiza p256dh/auth.
    """
    if not body.endpoint:
        raise HTTPException(status_code=400, detail="endpoint vazio")

    existing = await session.get(PushSubscription, body.endpoint)
    if existing is None:
        sub = PushSubscription(
            endpoint=body.endpoint,
            p256dh=body.keys.p256dh,
            auth=body.keys.auth,
            user_agent=body.user_agent,
        )
        session.add(sub)
    else:
        existing.p256dh = body.keys.p256dh
        existing.auth = body.keys.auth
        if body.user_agent is not None:
            existing.user_agent = body.user_agent
    await session.commit()
    log.info("Push subscription registrada: %s", body.endpoint[:50])
    return SubscribeResponse(ok=True)


@router.delete("/unsubscribe", response_model=SubscribeResponse)
async def unsubscribe(
    body: UnsubscribeRequest,
    session: AsyncSession = Depends(get_session),
) -> SubscribeResponse:
    """Remove uma subscription do DB. Idempotente."""
    await session.execute(
        delete(PushSubscription).where(PushSubscription.endpoint == body.endpoint)
    )
    await session.commit()
    return SubscribeResponse(ok=True)
