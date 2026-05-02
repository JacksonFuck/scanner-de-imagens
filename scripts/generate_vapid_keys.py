"""Gera um par de chaves VAPID (base64url) para Web Push.

Uso (uma vez por deploy):
    python scripts/generate_vapid_keys.py

Imprime SCANNER_VAPID_PUBLIC_KEY e SCANNER_VAPID_PRIVATE_KEY no formato
base64url, prontas para colar no .env / docker-compose.

Requer: cryptography (vem com pywebpush).
"""

from __future__ import annotations

import base64

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec


def _b64url(data: bytes) -> str:
    """base64url sem padding (formato exigido pelo Web Push / VAPID)."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def main() -> None:
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    # Private key: 32-byte raw scalar (formato esperado por pywebpush)
    private_numbers = private_key.private_numbers()
    private_raw = private_numbers.private_value.to_bytes(32, byteorder="big")

    # Public key: 65-byte uncompressed (0x04 || X || Y)
    public_raw = public_key.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint,
    )

    print("# VAPID keys — guarde a privada com cuidado.")
    print(f"SCANNER_VAPID_PUBLIC_KEY={_b64url(public_raw)}")
    print(f"SCANNER_VAPID_PRIVATE_KEY={_b64url(private_raw)}")
    print("SCANNER_VAPID_EMAIL=mailto:you@example.com")


if __name__ == "__main__":
    main()
