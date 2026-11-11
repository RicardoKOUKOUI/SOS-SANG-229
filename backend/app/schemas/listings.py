"""Professional, work, and marketplace schemas. Prices are display-only."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.social import AuthorBrief


class ProfessionalUpsert(BaseModel):
    headline: str = Field(min_length=2, max_length=160)
    organization: str | None = Field(default=None, max_length=160)
    city_label: str | None = Field(default=None, max_length=80)
    summary: str | None = Field(default=None, max_length=4000)

    @field_validator("headline", "organization", "city_label", "summary")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class ProfessionalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    headline: str
    organization: str | None = None
    city_label: str | None = None
    summary: str | None = None
    user: AuthorBrief


class JobCreate(BaseModel):
    title: str = Field(min_length=2, max_length=160)
    description: str | None = Field(default=None, max_length=4000)
    city_label: str | None = Field(default=None, max_length=80)

    @field_validator("title", "description", "city_label")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class JobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None = None
    city_label: str | None = None
    created_at: datetime
    created_by: AuthorBrief


class MarketCreate(BaseModel):
    title: str = Field(min_length=2, max_length=160)
    description: str | None = Field(default=None, max_length=4000)
    price_minor: int = Field(ge=0, le=100_000_000)

    @field_validator("title", "description")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class MarketRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None = None
    price_minor: int
    currency: str
    checkout_available: bool = False
    created_at: datetime
    created_by: AuthorBrief
