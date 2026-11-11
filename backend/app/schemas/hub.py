"""HUB Events + AI schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.social import AuthorBrief


class EventCreate(BaseModel):
    title: str = Field(min_length=2, max_length=160)
    description: str | None = Field(default=None, max_length=4000)
    location_label: str | None = Field(default=None, max_length=160)
    starts_at: datetime
    ends_at: datetime | None = None

    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Title required.")
        return cleaned


class EventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None = None
    location_label: str | None = None
    starts_at: datetime
    ends_at: datetime | None = None
    created_by: AuthorBrief


class AiStatusRead(BaseModel):
    configured: bool
    provider: str | None = None
    reason: str


class AiChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)

    @field_validator("message")
    @classmethod
    def strip_message(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Message required.")
        return cleaned


class AiChatResponse(BaseModel):
    reply: str
    provider: str
