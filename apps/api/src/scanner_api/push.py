"""Web Push wrapper — dispara notificação para 1 subscription.

Encapsula `pywebpush.webpush()`. Exceções HTTP do push service são tratadas:
- 410 Gone / 404 Not Found → subscription expirada (caller deve deletar do DB)
- Outras → log warning, retorna False mas não levanta

Caller é responsável por iterar sobre subscriptions e remover as expiradas.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

from pywebpush import WebPushException, webpush

from scanner_api.settings import get_settings

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class PushResult:
    """Resultado do envio: success + se a subscription deve ser removida."""

    success: bool
    expired: bool  # True se 410/404 — caller deve deletar


def send_push(
    endpoint: str,
    p256dh: str,
    auth: str,
    payload: dict[str, Any],
) -> PushResult:
    """Envia uma push notification a uma única subscription.

    Args:
        endpoint: URL do push service (Mozilla/Google/etc).
        p256dh: Chave pública da subscription (base64url).
        auth: Auth secret da subscription (base64url).
        payload: Dict serializável (vai como JSON no body).

    Returns:
        PushResult.success=True se o push service aceitou (2xx).
        PushResult.expired=True se o endpoint retornou 410/404 — caller
        deve deletar a subscription do DB.
    """
    settings = get_settings()
    subscription_info = {
        "endpoint": endpoint,
        "keys": {"p256dh": p256dh, "auth": auth},
    }
    vapid_email = settings.vapid_email
    if not vapid_email.startswith("mailto:"):
        vapid_email = f"mailto:{vapid_email}"

    try:
        webpush(
            subscription_info=subscription_info,
            data=json.dumps(payload),
            vapid_private_key=settings.vapid_private_key,
            vapid_claims={"sub": vapid_email},
        )
        return PushResult(success=True, expired=False)
    except WebPushException as exc:
        status = getattr(exc.response, "status_code", None) if exc.response else None
        if status in (404, 410):
            log.info("Push subscription expirada (status=%s): %s", status, endpoint)
            return PushResult(success=False, expired=True)
        log.warning("Push falhou (status=%s) para %s: %s", status, endpoint, exc)
        return PushResult(success=False, expired=False)
    except Exception as exc:
        log.warning("Push erro inesperado para %s: %s", endpoint, exc)
        return PushResult(success=False, expired=False)
