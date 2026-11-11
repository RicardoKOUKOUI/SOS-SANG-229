"""Create messaging + communities tables (Phase 4).

Revision ID: 006_messaging_communities
Revises: 005_social_light
Create Date: 2026-11-11
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "006_messaging_communities"
down_revision: Union[str, Sequence[str], None] = "005_social_light"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(name: str) -> bool:
    bind = op.get_bind()
    return name in sa.inspect(bind).get_table_names()


def upgrade() -> None:
    if not _has_table("conversations"):
        op.create_table(
            "conversations",
            sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
            sa.Column("kind", sa.String(length=16), nullable=False),
            sa.Column("title", sa.String(length=120), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _has_table("conversation_members"):
        op.create_table(
            "conversation_members",
            sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
            sa.Column("conversation_id", sa.Uuid(), nullable=False),
            sa.Column("user_id", sa.Uuid(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("conversation_id", "user_id", name="uq_conversation_member"),
        )
        op.create_index("ix_conversation_members_user_id", "conversation_members", ["user_id"])
    if not _has_table("direct_messages"):
        op.create_table(
            "direct_messages",
            sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
            sa.Column("conversation_id", sa.Uuid(), nullable=False),
            sa.Column("sender_id", sa.Uuid(), nullable=False),
            sa.Column("body", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["sender_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            "ix_direct_messages_conversation_created",
            "direct_messages",
            ["conversation_id", "created_at"],
        )
    if not _has_table("communities"):
        op.create_table(
            "communities",
            sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
            sa.Column("name", sa.String(length=120), nullable=False),
            sa.Column("slug", sa.String(length=64), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("is_public", sa.Boolean(), server_default=sa.text("true"), nullable=False),
            sa.Column("owner_id", sa.Uuid(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("slug"),
        )
    if not _has_table("community_members"):
        op.create_table(
            "community_members",
            sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
            sa.Column("community_id", sa.Uuid(), nullable=False),
            sa.Column("user_id", sa.Uuid(), nullable=False),
            sa.Column("role", sa.String(length=24), server_default="member", nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.ForeignKeyConstraint(["community_id"], ["communities.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("community_id", "user_id", name="uq_community_member"),
        )
        op.create_index("ix_community_members_user_id", "community_members", ["user_id"])
    if not _has_table("community_rooms"):
        op.create_table(
            "community_rooms",
            sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
            sa.Column("community_id", sa.Uuid(), nullable=False),
            sa.Column("name", sa.String(length=80), nullable=False),
            sa.Column("slug", sa.String(length=64), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.ForeignKeyConstraint(["community_id"], ["communities.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("community_id", "slug", name="uq_community_room_slug"),
        )
    if not _has_table("community_messages"):
        op.create_table(
            "community_messages",
            sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
            sa.Column("room_id", sa.Uuid(), nullable=False),
            sa.Column("author_id", sa.Uuid(), nullable=False),
            sa.Column("body", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["room_id"], ["community_rooms.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            "ix_community_messages_room_created",
            "community_messages",
            ["room_id", "created_at"],
        )


def downgrade() -> None:
    for table in (
        "community_messages",
        "community_rooms",
        "community_members",
        "communities",
        "direct_messages",
        "conversation_members",
        "conversations",
    ):
        if _has_table(table):
            op.drop_table(table)
