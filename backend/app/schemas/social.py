"""Social-light request/response schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PostCreate(BaseModel):
    body: str = Field(min_length=1, max_length=4000)

    @field_validator("body")
    @classmethod
    def strip_body(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Post body cannot be empty.")
        return cleaned


class AuthorBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    display_name: str


class PostRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    body: str
    created_at: datetime
    author: AuthorBrief
    like_count: int = 0
    comment_count: int = 0
    liked_by_me: bool = False


class CommentCreate(BaseModel):
    body: str = Field(min_length=1, max_length=2000)

    @field_validator("body")
    @classmethod
    def strip_body(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Comment cannot be empty.")
        return cleaned


class CommentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    body: str
    created_at: datetime
    author: AuthorBrief


class LikeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user: AuthorBrief


class FollowRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user: AuthorBrief


class ExploreResults(BaseModel):
    people: list[AuthorBrief]
    posts: list[PostRead]
