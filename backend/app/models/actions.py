"""DOXAMI ACTIONS — projects, tasks, team. Progress is computed, never faked."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.social import Post
    from app.models.user import User


class ActionProject(TimestampMixin, Base):
    __tablename__ = "action_projects"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    source_post_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("posts.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_by: Mapped["User"] = relationship()
    source_post: Mapped["Post | None"] = relationship()
    tasks: Mapped[list["ActionTask"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    members: Mapped[list["ActionMember"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )


class ActionTask(TimestampMixin, Base):
    __tablename__ = "action_tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("action_projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="todo")
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    assignee_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    project: Mapped[ActionProject] = relationship(back_populates="tasks")
    assignee: Mapped["User | None"] = relationship()


class ActionMember(TimestampMixin, Base):
    __tablename__ = "action_members"
    __table_args__ = (
        UniqueConstraint("project_id", "user_id", name="uq_action_member"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("action_projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(String(16), nullable=False, default="member")

    project: Mapped[ActionProject] = relationship(back_populates="members")
    user: Mapped["User"] = relationship()
