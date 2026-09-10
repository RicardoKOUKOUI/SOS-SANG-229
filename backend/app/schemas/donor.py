"""Pydantic schemas for donors (User / Donneur)."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.enums import BloodGroup
from app.schemas.common import SENSITIVE_NOTE, GeoPoint


class DonorCreate(BaseModel):
    display_name: str = Field(min_length=1, max_length=255, examples=["Donneur Demo"])
    blood_group: BloodGroup = Field(description=SENSITIVE_NOTE, examples=["O+"])
    phone: str = Field(
        min_length=10,
        max_length=14,
        description=SENSITIVE_NOTE + " Numéro béninois à 10 chiffres commençant par 01.",
        examples=["0190123456"],
    )
    city: str = Field(min_length=1, max_length=120, examples=["Zone Demo"])
    location: GeoPoint | None = Field(default=None, description=SENSITIVE_NOTE)
    is_available: bool = True

    @field_validator("phone")
    @classmethod
    def benin_ten_digits(cls, value: str) -> str:
        digits = "".join(ch for ch in value if ch.isdigit())
        # Accept +229XXXXXXXXXX by keeping last 10 national digits
        if digits.startswith("229") and len(digits) == 13:
            digits = digits[3:]
        if len(digits) != 10 or not digits.startswith("01"):
            raise ValueError(
                "Le numéro béninois doit contenir 10 chiffres et commencer par 01"
            )
        return digits


class DonorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    display_name: str
    blood_group: BloodGroup = Field(description=SENSITIVE_NOTE)
    phone: str = Field(description=SENSITIVE_NOTE)
    city: str
    location: GeoPoint | None = Field(default=None, description=SENSITIVE_NOTE)
    is_available: bool
    created_at: datetime
    updated_at: datetime


class DonorPublic(BaseModel):
    """API create/read payload. Phone and GPS are omitted."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    display_name: str
    blood_group: BloodGroup = Field(description=SENSITIVE_NOTE)
    city: str
    is_available: bool
    created_at: datetime
    updated_at: datetime
