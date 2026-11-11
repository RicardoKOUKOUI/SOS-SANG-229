"""Password hashing and JWT helpers for DOXAMI auth."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import bcrypt
import jwt

from app.config import get_settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except ValueError:
        return False


def create_access_token(
    *,
    user_id: UUID,
    expires_minutes: int | None = None,
    mfa: bool = False,
) -> str:
    settings = get_settings()
    secret = settings.jwt_secret
    if not secret:
        raise RuntimeError(
            "JWT_SECRET is not set. Copy .env.example to .env and set a local secret."
        )
    minutes = (
        expires_minutes
        if expires_minutes is not None
        else settings.access_token_expire_minutes
    )
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=minutes),
        "typ": "access",
        "mfa": mfa,
    }
    return jwt.encode(payload, secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    secret = settings.jwt_secret
    if not secret:
        raise RuntimeError("JWT_SECRET is not set.")
    return jwt.decode(token, secret, algorithms=[settings.jwt_algorithm])
