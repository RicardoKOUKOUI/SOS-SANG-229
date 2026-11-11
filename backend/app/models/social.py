"""DOXAMI social-light models: posts, follows, likes, comments."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Text, UniqueConstraint, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class Post(TimestampMixin, Base):
    """Text publication (Phase 3 — no media upload yet)."""

    __tablename__ = "posts"
    __table_args__ = (Index("ix_posts_author_id_created_at", "author_id", "created_at"),)

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)

    author: Mapped["User"] = relationship()
    likes: Mapped[list["PostLike"]] = relationship(
        back_populates="post",
        cascade="all, delete-orphan",
    )
    comments: Mapped[list["PostComment"]] = relationship(
        back_populates="post",
        cascade="all, delete-orphan",
    )


class Follow(TimestampMixin, Base):
    """User A follows user B."""

    __tablename__ = "follows"
    __table_args__ = (
        UniqueConstraint("follower_id", "following_id", name="uq_follows_pair"),
        Index("ix_follows_following_id", "following_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    follower_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    following_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )


class PostLike(TimestampMixin, Base):
    __tablename__ = "post_likes"
    __table_args__ = (
        UniqueConstraint("user_id", "post_id", name="uq_post_likes_user_post"),
        Index("ix_post_likes_post_id", "post_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    post_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
    )

    post: Mapped[Post] = relationship(back_populates="likes")


class PostComment(TimestampMixin, Base):
    __tablename__ = "post_comments"
    __table_args__ = (Index("ix_post_comments_post_id_created_at", "post_id", "created_at"),)

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    post_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)

    post: Mapped[Post] = relationship(back_populates="comments")
    author: Mapped["User"] = relationship()
