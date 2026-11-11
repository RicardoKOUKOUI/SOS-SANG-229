"""Create ACTIONS tables (projects, tasks, members).

Revision ID: 008_actions
Revises: 007_hub_events
Create Date: 2026-11-11
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "008_actions"
down_revision: Union[str, Sequence[str], None] = "007_hub_events"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(name: str) -> bool:
    return name in sa.inspect(op.get_bind()).get_table_names()


def upgrade() -> None:
    if not _has_table("action_projects"):
        op.create_table(
            "action_projects",
            sa.Column(
                "id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False
            ),
            sa.Column("title", sa.String(length=160), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("created_by_id", sa.Uuid(), nullable=False),
            sa.Column("source_post_id", sa.Uuid(), nullable=True),
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
            sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["source_post_id"], ["posts.id"], ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _has_table("action_tasks"):
        op.create_table(
            "action_tasks",
            sa.Column(
                "id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False
            ),
            sa.Column("project_id", sa.Uuid(), nullable=False),
            sa.Column("title", sa.String(length=200), nullable=False),
            sa.Column("status", sa.String(length=16), nullable=False),
            sa.Column("position", sa.Integer(), nullable=False),
            sa.Column("assignee_id", sa.Uuid(), nullable=True),
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
            sa.ForeignKeyConstraint(["assignee_id"], ["users.id"], ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["project_id"], ["action_projects.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_action_tasks_project_id", "action_tasks", ["project_id"])

    if not _has_table("action_members"):
        op.create_table(
            "action_members",
            sa.Column(
                "id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False
            ),
            sa.Column("project_id", sa.Uuid(), nullable=False),
            sa.Column("user_id", sa.Uuid(), nullable=False),
            sa.Column("role", sa.String(length=16), nullable=False),
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
            sa.ForeignKeyConstraint(["project_id"], ["action_projects.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("project_id", "user_id", name="uq_action_member"),
        )


def downgrade() -> None:
    for name in ("action_members", "action_tasks", "action_projects"):
        if _has_table(name):
            op.drop_table(name)
