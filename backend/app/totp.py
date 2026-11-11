"""RFC 6238 TOTP (SHA-1, 30s, 6 digits). Stdlib only."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import struct
import time
from urllib.parse import quote


def generate_secret() -> str:
    return base64.b32encode(os.urandom(20)).decode("ascii").rstrip("=")


def _counter_code(secret: str, counter: int) -> str:
    padded = secret.strip().upper()
    padded += "=" * ((8 - len(padded) % 8) % 8)
    key = base64.b32decode(padded, casefold=True)
    digest = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    binary = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return f"{binary % 1_000_000:06d}"


def verify_totp(secret: str, code: str, *, now: float | None = None) -> bool:
    cleaned = code.strip()
    if len(cleaned) != 6 or not cleaned.isdigit():
        return False
    moment = time.time() if now is None else now
    counter = int(moment) // 30
    for drift in (-1, 0, 1):
        if hmac.compare_digest(_counter_code(secret, counter + drift), cleaned):
            return True
    return False


def current_code(secret: str, *, now: float | None = None) -> str:
    moment = time.time() if now is None else now
    return _counter_code(secret, int(moment) // 30)


def otpauth_uri(*, secret: str, username: str) -> str:
    label = quote(f"DOXAMI:{username}")
    return (
        f"otpauth://totp/{label}?secret={secret}&issuer=DOXAMI&algorithm=SHA1&digits=6&period=30"
    )
