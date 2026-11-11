"""Creator studio + monetization status schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.social import AuthorBrief


class CreatorProfileUpsert(BaseModel):
    pitch: str | None = Field(default=None, max_length=2000)
    focus: str | None = Field(default=None, max_length=80)
    accepting_collabs: bool = False

    @field_validator("pitch", "focus")
    @classmethod
    def strip_optional(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class CreatorProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    pitch: str | None = None
    focus: str | None = None
    accepting_collabs: bool
    user: AuthorBrief


class MonetizationStatusRead(BaseModel):
    ads_enabled: bool
    premium_enabled: bool
    psp_configured: bool
    payouts_ready: bool
    earnings_minor: int
    currency: str
    reason: str


class PremiumPlanRead(BaseModel):
    code: str
    name: str
    checkout_available: bool
    note: str
