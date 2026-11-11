"""Create DOXAMI users table for auth/profiles.

Revision ID: 004_users
Revises: 003_urgency_matches
Create Date: 2026-11-11
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "004_users"
down_revision: Union[str, Sequence[str], None] = "003_urgency_matches"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return name in inspector.get_table_names()


def upgrade() -> None:
    if _has_table("users"):
        return
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column(
            "email",
            sa.String(length=320),
            nullable=False,
            comment="SENSITIVE — never log in cleartext.",
        ),
        sa.Column("username", sa.String(length=32), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column(
            "password_hash",
            sa.String(length=255),
            nullable=False,
            comment="SENSITIVE — never log in cleartext.",
        ),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column(
            "phone",
            sa.String(length=20),
            nullable=True,
            comment="SENSITIVE — never log in cleartext.",
        ),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "email_verified",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
        sa.UniqueConstraint("phone"),
        comment="DOXAMI users. email/phone/password_hash are SENSITIVE.",
    )
    op.create_index("ix_users_username", "users", ["username"], unique=False)


def downgrade() -> None:
    if _has_table("users"):
        op.drop_index("ix_users_username", table_name="users")
        op.drop_table("users")
