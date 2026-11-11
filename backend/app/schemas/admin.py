"""Admin API schemas. No email, phone, or TOTP secret in list responses."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class BootstrapRequest(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    token: str = Field(min_length=1, max_length=200)


class MfaEnrollRead(BaseModel):
    secret: str
    otpauth_uri: str
    enabled: bool = False


class MfaCodeRequest(BaseModel):
    code: str = Field(min_length=6, max_length=6)


class DashboardRead(BaseModel):
    users: int
    admins: int
    posts: int
    hidden_posts: int
    flags_enabled: int


class AdminUserRead(BaseModel):
    id: UUID
    username: str
    display_name: str
    role: str
    is_active: bool
    totp_enabled: bool


class AdminUserUpdate(BaseModel):
    is_active: bool


class ModerationPostRead(BaseModel):
    id: UUID
    body: str
    hidden: bool
    author_username: str
    created_at: datetime


class FlagRead(BaseModel):
    key: str
    enabled: bool
    note: str | None = None
    checkout_unchanged: bool = True


class FlagUpdate(BaseModel):
    enabled: bool


class AuditLogRead(BaseModel):
    id: UUID
    action: str
    target_type: str | None = None
    target_id: str | None = None
    actor_username: str
    created_at: datetime
