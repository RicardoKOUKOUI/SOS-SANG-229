"""Admin role, TOTP, post visibility, and audit log.

Revision ID: 011_admin
Revises: 010_listings
Create Date: 2026-11-11
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "011_admin"
down_revision: Union[str, Sequence[str], None] = "010_listings"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _columns(table: str) -> set[str]:
    return {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table)}


def _has_table(name: str) -> bool:
    return name in sa.inspect(op.get_bind()).get_table_names()


def upgrade() -> None:
    user_columns = _columns("users")
    if "role" not in user_columns:
        op.add_column(
            "users",
            sa.Column("role", sa.String(length=16), nullable=False, server_default="member"),
        )
    if "totp_secret" not in user_columns:
        op.add_column("users", sa.Column("totp_secret", sa.String(length=64), nullable=True))
    if "totp_enabled" not in user_columns:
        op.add_column(
            "users",
            sa.Column("totp_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        )
    if "hidden" not in _columns("posts"):
        op.add_column(
            "posts",
            sa.Column("hidden", sa.Boolean(), nullable=False, server_default=sa.false()),
        )
    if not _has_table("admin_audit_logs"):
        op.create_table(
            "admin_audit_logs",
            sa.Column(
                "id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False
            ),
            sa.Column("actor_id", sa.Uuid(), nullable=False),
            sa.Column("action", sa.String(length=64), nullable=False),
            sa.Column("target_type", sa.String(length=32), nullable=True),
            sa.Column("target_id", sa.String(length=64), nullable=True),
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
            sa.ForeignKeyConstraint(["actor_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )


def downgrade() -> None:
    if _has_table("admin_audit_logs"):
        op.drop_table("admin_audit_logs")
    post_columns = _columns("posts")
    if "hidden" in post_columns:
        op.drop_column("posts", "hidden")
    user_columns = _columns("users")
    for name in ("totp_enabled", "totp_secret", "role"):
        if name in user_columns:
            op.drop_column("users", name)
