"""Messaging + communities schemas."""

from __future__ import annotations

import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.social import AuthorBrief

_SLUG_RE = re.compile(r"^[a-z0-9-]{3,64}$")


class MessageCreate(BaseModel):
    body: str = Field(min_length=1, max_length=4000)

    @field_validator("body")
    @classmethod
    def strip_body(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Message cannot be empty.")
        return cleaned


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    body: str
    created_at: datetime
    sender: AuthorBrief


class DirectThreadCreate(BaseModel):
    username: str = Field(min_length=3, max_length=32)


class GroupThreadCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    usernames: list[str] = Field(default_factory=list, max_length=20)

    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Title required.")
        return cleaned


class ThreadRead(BaseModel):
    id: UUID
    kind: str
    title: str | None = None
    members: list[AuthorBrief]
    last_message: MessageRead | None = None


class CommunityCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    slug: str = Field(min_length=3, max_length=64)
    description: str | None = Field(default=None, max_length=2000)
    is_public: bool = True

    @field_validator("slug")
    @classmethod
    def normalize_slug(cls, value: str) -> str:
        slug = value.strip().lower()
        if not _SLUG_RE.fullmatch(slug):
            raise ValueError("Slug must be 3–64 chars: a-z, 0-9, hyphen.")
        return slug

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Name required.")
        return cleaned


class CommunityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    description: str | None = None
    is_public: bool
    owner: AuthorBrief
    member_count: int = 0
    is_member: bool = False


class RoomCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    slug: str = Field(min_length=2, max_length=64)

    @field_validator("slug")
    @classmethod
    def normalize_slug(cls, value: str) -> str:
        slug = value.strip().lower()
        if not _SLUG_RE.fullmatch(slug):
            raise ValueError("Slug must be 3–64 chars: a-z, 0-9, hyphen.")
        return slug


class RoomRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str


class CommunityMessageRead(BaseModel):
    id: UUID
    body: str
    created_at: datetime
    author: AuthorBrief
