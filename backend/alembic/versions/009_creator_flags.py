"""Creator profiles and monetization feature flags.

Revision ID: 009_creator_flags
Revises: 008_actions
Create Date: 2026-11-11
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "009_creator_flags"
down_revision: Union[str, Sequence[str], None] = "008_actions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(name: str) -> bool:
    return name in sa.inspect(op.get_bind()).get_table_names()


def upgrade() -> None:
    if not _has_table("creator_profiles"):
        op.create_table(
            "creator_profiles",
            sa.Column(
                "id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False
            ),
            sa.Column("user_id", sa.Uuid(), nullable=False),
            sa.Column("pitch", sa.Text(), nullable=True),
            sa.Column("focus", sa.String(length=80), nullable=True),
            sa.Column("accepting_collabs", sa.Boolean(), nullable=False, server_default=sa.false()),
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
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("user_id"),
        )

    if not _has_table("feature_flags"):
        op.create_table(
            "feature_flags",
            sa.Column("key", sa.String(length=64), nullable=False),
            sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("note", sa.String(length=240), nullable=True),
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
            sa.PrimaryKeyConstraint("key"),
        )
        op.bulk_insert(
            sa.table(
                "feature_flags",
                sa.column("key", sa.String),
                sa.column("enabled", sa.Boolean),
                sa.column("note", sa.String),
            ),
            [
                {
                    "key": "ads_enabled",
                    "enabled": False,
                    "note": "Ad delivery off until an ad network is configured.",
                },
                {
                    "key": "premium_enabled",
                    "enabled": False,
                    "note": "Premium checkout off until a PSP is configured.",
                },
            ],
        )


def downgrade() -> None:
    for name in ("feature_flags", "creator_profiles"):
        if _has_table(name):
            op.drop_table(name)
