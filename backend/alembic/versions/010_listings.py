"""Professional profiles, jobs, and marketplace listings.

Revision ID: 010_listings
Revises: 009_creator_flags
Create Date: 2026-11-11
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "010_listings"
down_revision: Union[str, Sequence[str], None] = "009_creator_flags"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(name: str) -> bool:
    return name in sa.inspect(op.get_bind()).get_table_names()


def _timestamps() -> list[sa.Column]:
    return [
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
    ]


def upgrade() -> None:
    if not _has_table("professional_profiles"):
        op.create_table(
            "professional_profiles",
            sa.Column(
                "id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False
            ),
            sa.Column("user_id", sa.Uuid(), nullable=False),
            sa.Column("headline", sa.String(length=160), nullable=False),
            sa.Column("organization", sa.String(length=160), nullable=True),
            sa.Column("city_label", sa.String(length=80), nullable=True),
            sa.Column("summary", sa.Text(), nullable=True),
            *_timestamps(),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("user_id"),
        )

    if not _has_table("job_listings"):
        op.create_table(
            "job_listings",
            sa.Column(
                "id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False
            ),
            sa.Column("title", sa.String(length=160), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("city_label", sa.String(length=80), nullable=True),
            sa.Column("created_by_id", sa.Uuid(), nullable=False),
            *_timestamps(),
            sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _has_table("market_listings"):
        op.create_table(
            "market_listings",
            sa.Column(
                "id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False
            ),
            sa.Column("title", sa.String(length=160), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("price_minor", sa.Integer(), nullable=False),
            sa.Column("currency", sa.String(length=8), nullable=False),
            sa.Column("created_by_id", sa.Uuid(), nullable=False),
            *_timestamps(),
            sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )


def downgrade() -> None:
    for name in ("market_listings", "job_listings", "professional_profiles"):
        if _has_table(name):
            op.drop_table(name)
