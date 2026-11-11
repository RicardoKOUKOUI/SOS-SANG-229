"""DOXAMI admin: RBAC, TOTP, public-post moderation, flags, audit. No private messages."""

from __future__ import annotations

import hmac
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.config import get_settings
from app.db import get_db
from app.deps import require_admin, require_admin_role
from app.models.admin import AdminAuditLog
from app.models.creator import FeatureFlag
from app.models.social import Post
from app.models.user import User
from app.schemas.admin import (
    AdminUserRead,
    AdminUserUpdate,
    AuditLogRead,
    BootstrapRequest,
    DashboardRead,
    FlagRead,
    FlagUpdate,
    MfaCodeRequest,
    MfaEnrollRead,
    ModerationPostRead,
)
from app.schemas.auth import TokenResponse
from app.security import create_access_token
from app.totp import generate_secret, otpauth_uri, verify_totp

router = APIRouter(prefix="/admin", tags=["admin"])

_FLAG_KEYS = {"ads_enabled", "premium_enabled"}


def _audit(
    db: Session,
    *,
    actor: User,
    action: str,
    target_type: str | None = None,
    target_id: str | None = None,
) -> None:
    db.add(
        AdminAuditLog(
            actor_id=actor.id,
            action=action,
            target_type=target_type,
            target_id=target_id,
        )
    )


def _user_read(user: User) -> AdminUserRead:
    return AdminUserRead(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        role=user.role,
        is_active=user.is_active,
        totp_enabled=user.totp_enabled,
    )


@router.post("/bootstrap", response_model=AdminUserRead)
def bootstrap_admin(
    payload: BootstrapRequest,
    db: Session = Depends(get_db),
) -> AdminUserRead:
    settings = get_settings()
    expected = settings.doxami_admin_bootstrap_token.strip()
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin bootstrap token is not configured.",
        )
    if not hmac.compare_digest(payload.token.strip(), expected):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid bootstrap token.")
    existing_admin = db.scalar(select(User.id).where(User.role == "admin").limit(1))
    if existing_admin is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An admin already exists.")
    user = db.scalar(select(User).where(User.username == payload.username.strip().lower()))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    user.role = "admin"
    _audit(db, actor=user, action="admin.bootstrap", target_type="user", target_id=str(user.id))
    db.commit()
    db.refresh(user)
    return _user_read(user)


@router.post("/mfa/enroll", response_model=MfaEnrollRead)
def enroll_mfa(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin_role),
) -> MfaEnrollRead:
    if admin.totp_enabled:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="2FA is already enabled.")
    secret = generate_secret()
    admin.totp_secret = secret
    admin.totp_enabled = False
    db.commit()
    return MfaEnrollRead(secret=secret, otpauth_uri=otpauth_uri(secret=secret, username=admin.username))


@router.post("/mfa/confirm", response_model=TokenResponse)
def confirm_mfa(
    payload: MfaCodeRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin_role),
) -> TokenResponse:
    if admin.totp_enabled:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="2FA is already enabled.")
    if not admin.totp_secret or not verify_totp(admin.totp_secret, payload.code):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication code.")
    admin.totp_enabled = True
    _audit(db, actor=admin, action="admin.mfa_enabled", target_type="user", target_id=str(admin.id))
    db.commit()
    return TokenResponse(access_token=create_access_token(user_id=admin.id, mfa=True))


@router.post("/mfa/verify", response_model=TokenResponse)
def verify_mfa(
    payload: MfaCodeRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin_role),
) -> TokenResponse:
    if not admin.totp_enabled or not admin.totp_secret:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Enroll 2FA before verifying.")
    if not verify_totp(admin.totp_secret, payload.code):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication code.")
    return TokenResponse(access_token=create_access_token(user_id=admin.id, mfa=True))


@router.get("/dashboard", response_model=DashboardRead)
def dashboard(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> DashboardRead:
    return DashboardRead(
        users=db.scalar(select(func.count()).select_from(User)) or 0,
        admins=db.scalar(select(func.count()).select_from(User).where(User.role == "admin")) or 0,
        posts=db.scalar(select(func.count()).select_from(Post)) or 0,
        hidden_posts=db.scalar(
            select(func.count()).select_from(Post).where(Post.hidden.is_(True))
        )
        or 0,
        flags_enabled=db.scalar(
            select(func.count()).select_from(FeatureFlag).where(FeatureFlag.enabled.is_(True))
        )
        or 0,
    )


@router.get("/users", response_model=list[AdminUserRead])
def list_users(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> list[AdminUserRead]:
    users = db.scalars(select(User).order_by(User.created_at.desc()).limit(100)).all()
    return [_user_read(user) for user in users]


@router.patch("/users/{user_id}", response_model=AdminUserRead)
def update_user(
    user_id: UUID,
    payload: AdminUserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> AdminUserRead:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    if user.id == admin.id and payload.is_active is False:
        raise HTTPException(status_code=400, detail="You cannot deactivate your own admin account.")
    user.is_active = payload.is_active
    _audit(
        db,
        actor=admin,
        action="user.deactivate" if not payload.is_active else "user.activate",
        target_type="user",
        target_id=str(user.id),
    )
    db.commit()
    db.refresh(user)
    return _user_read(user)


@router.get("/moderation/posts", response_model=list[ModerationPostRead])
def list_posts_for_moderation(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> list[ModerationPostRead]:
    posts = db.scalars(
        select(Post)
        .options(selectinload(Post.author))
        .order_by(Post.created_at.desc())
        .limit(50)
    ).all()
    return [
        ModerationPostRead(
            id=post.id,
            body=post.body,
            hidden=post.hidden,
            author_username=post.author.username,
            created_at=post.created_at,
        )
        for post in posts
    ]


def _set_hidden(db: Session, admin: User, post_id: UUID, hidden: bool) -> ModerationPostRead:
    post = db.scalar(select(Post).options(selectinload(Post.author)).where(Post.id == post_id))
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found.")
    post.hidden = hidden
    _audit(
        db,
        actor=admin,
        action="post.hide" if hidden else "post.restore",
        target_type="post",
        target_id=str(post.id),
    )
    db.commit()
    db.refresh(post)
    return ModerationPostRead(
        id=post.id,
        body=post.body,
        hidden=post.hidden,
        author_username=post.author.username,
        created_at=post.created_at,
    )


@router.post("/moderation/posts/{post_id}/hide", response_model=ModerationPostRead)
def hide_post(
    post_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> ModerationPostRead:
    return _set_hidden(db, admin, post_id, True)


@router.post("/moderation/posts/{post_id}/restore", response_model=ModerationPostRead)
def restore_post(
    post_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> ModerationPostRead:
    return _set_hidden(db, admin, post_id, False)


@router.get("/flags", response_model=list[FlagRead])
def list_flags(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> list[FlagRead]:
    rows = db.scalars(select(FeatureFlag).order_by(FeatureFlag.key.asc())).all()
    return [
        FlagRead(key=row.key, enabled=row.enabled, note=row.note, checkout_unchanged=True)
        for row in rows
    ]


@router.patch("/flags/{key}", response_model=FlagRead)
def update_flag(
    key: str,
    payload: FlagUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> FlagRead:
    if key not in _FLAG_KEYS:
        raise HTTPException(status_code=404, detail="Flag not found.")
    row = db.get(FeatureFlag, key)
    if row is None:
        row = FeatureFlag(key=key, enabled=payload.enabled, note="Set by admin.")
        db.add(row)
    row.enabled = payload.enabled
    _audit(db, actor=admin, action="flag.update", target_type="flag", target_id=key)
    db.commit()
    db.refresh(row)
    return FlagRead(
        key=row.key,
        enabled=row.enabled,
        note=(
            "Flag stored. Premium/ads flags do not enable checkout or payouts."
        ),
        checkout_unchanged=True,
    )


@router.get("/logs", response_model=list[AuditLogRead])
def list_logs(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> list[AuditLogRead]:
    rows = db.scalars(
        select(AdminAuditLog)
        .options(selectinload(AdminAuditLog.actor))
        .order_by(AdminAuditLog.created_at.desc())
        .limit(100)
    ).all()
    return [
        AuditLogRead(
            id=row.id,
            action=row.action,
            target_type=row.target_type,
            target_id=row.target_id,
            actor_username=row.actor.username,
            created_at=row.created_at,
        )
        for row in rows
    ]
