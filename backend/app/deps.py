"""FastAPI dependencies (auth)."""

from __future__ import annotations

from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.security import decode_access_token

_bearer = HTTPBearer(auto_error=False)


def _user_from_credentials(
    credentials: HTTPAuthorizationCredentials | None,
    db: Session,
) -> User | None:
    if credentials is None or credentials.scheme.lower() != "bearer":
        return None
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = UUID(str(payload["sub"]))
    except Exception:  # noqa: BLE001 — invalid token → anonymous
        return None
    return db.scalar(select(User).where(User.id == user_id, User.is_active.is_(True)))


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    user = _user_from_credentials(credentials, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User | None:
    return _user_from_credentials(credentials, db)


def _payload_or_401(
    credentials: HTTPAuthorizationCredentials | None,
) -> dict:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return decode_access_token(credentials.credentials)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def require_admin_role(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    """Admin role only. Used for TOTP enrollment before a second factor exists."""
    payload = _payload_or_401(credentials)
    try:
        user_id = UUID(str(payload["sub"]))
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.") from exc
    user = db.scalar(select(User).where(User.id == user_id, User.is_active.is_(True)))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required.")
    return user


def require_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    """Admin role plus a token issued after a valid TOTP check."""
    payload = _payload_or_401(credentials)
    user = require_admin_role(credentials, db)
    if payload.get("mfa") is not True:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin 2FA required.",
        )
    return user
