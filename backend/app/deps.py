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
