"""Donor (User / Donneur) ORM model."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, Index, String, Text, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums import BloodGroup
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.donation import DonationConfirmation
    from app.models.match import UrgencyMatch

_SENSITIVE = "SENSITIVE — never log in cleartext."


class Donor(TimestampMixin, Base):
    """Registered blood donor.

    Sensitive columns: ``phone``, ``blood_group``, ``location`` (GPS WKT).
    """

    __tablename__ = "donors"
    __table_args__ = (
        Index("ix_donors_blood_group", "blood_group"),
        Index("ix_donors_city", "city"),
        {"comment": "Blood donors. phone, blood_group, location are SENSITIVE."},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    blood_group: Mapped[BloodGroup] = mapped_column(
        Enum(
            BloodGroup,
            name="blood_group",
            values_callable=lambda members: [member.value for member in members],
        ),
        nullable=False,
        comment=f"Blood group. {_SENSITIVE}",
    )
    phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True,
        comment=f"E.164-style phone. {_SENSITIVE}",
    )
    city: Mapped[str] = mapped_column(String(120), nullable=False)
    location: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment=f"Optional GPS as WKT POINT(lng lat). {_SENSITIVE}",
    )
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    donation_confirmations: Mapped[list["DonationConfirmation"]] = relationship(
        back_populates="donor",
    )
    urgency_matches: Mapped[list["UrgencyMatch"]] = relationship(
        back_populates="donor",
    )
