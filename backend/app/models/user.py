"""DOXAMI user account (auth + minimal profile)."""

import uuid

from sqlalchemy import Boolean, Index, String, Text, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin

_SENSITIVE = "SENSITIVE — never log in cleartext."


class User(TimestampMixin, Base):
    """Registered DOXAMI account.

    Sensitive columns: ``email``, ``password_hash``, optional ``phone``.
    """

    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_username", "username"),
        {"comment": "DOXAMI users. email/phone/password_hash are SENSITIVE."},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    email: Mapped[str] = mapped_column(
        String(320),
        nullable=False,
        unique=True,
        comment=f"Login email. {_SENSITIVE}",
    )
    username: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment=f"Password hash. {_SENSITIVE}",
    )
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        unique=True,
        comment=f"Optional phone. {_SENSITIVE}",
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    role: Mapped[str] = mapped_column(
        String(16), nullable=False, default="member", server_default=text("'member'")
    )
    totp_secret: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        comment=f"TOTP shared secret. {_SENSITIVE}",
    )
    totp_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
