"""Create MVP schema without PostGIS (Text WKT locations).

Revision ID: 001_mvp_schema
Revises:
Create Date: 2026-09-09

Locations are stored as nullable Text WKT ``POINT(lng lat)``.
No PostGIS extension or GiST indexes — works on Railway standard Postgres.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_mvp_schema"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

BLOOD_GROUP_VALUES = ("O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-")
URGENCY_STATUS_VALUES = ("open", "alerting", "fulfilled", "cancelled")
DONATION_STATUS_VALUES = ("pending", "confirmed", "cancelled")


def _has_table(name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return name in inspector.get_table_names()


def upgrade() -> None:
    blood_group = postgresql.ENUM(*BLOOD_GROUP_VALUES, name="blood_group")
    urgency_status = postgresql.ENUM(*URGENCY_STATUS_VALUES, name="urgency_status")
    donation_status = postgresql.ENUM(*DONATION_STATUS_VALUES, name="donation_status")
    blood_group.create(op.get_bind(), checkfirst=True)
    urgency_status.create(op.get_bind(), checkfirst=True)
    donation_status.create(op.get_bind(), checkfirst=True)

    if not _has_table("donors"):
        op.create_table(
            "donors",
            sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
            sa.Column("display_name", sa.String(length=255), nullable=False),
            sa.Column(
                "blood_group",
                postgresql.ENUM(*BLOOD_GROUP_VALUES, name="blood_group", create_type=False),
                nullable=False,
                comment="SENSITIVE — never log in cleartext.",
            ),
            sa.Column(
                "phone",
                sa.String(length=20),
                nullable=False,
                comment="SENSITIVE — never log in cleartext.",
            ),
            sa.Column("city", sa.String(length=120), nullable=False),
            sa.Column(
                "location",
                sa.Text(),
                nullable=True,
                comment="SENSITIVE GPS WKT POINT(lng lat) — never log in cleartext.",
            ),
            sa.Column("is_available", sa.Boolean(), nullable=False, server_default=sa.true()),
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
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("phone"),
            comment="Blood donors. phone, blood_group, location are SENSITIVE.",
        )
        op.create_index("ix_donors_blood_group", "donors", ["blood_group"])
        op.create_index("ix_donors_city", "donors", ["city"])

    if not _has_table("hospitals"):
        op.create_table(
            "hospitals",
            sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("city", sa.String(length=120), nullable=False),
            sa.Column(
                "location",
                sa.Text(),
                nullable=True,
                comment="SENSITIVE GPS WKT POINT(lng lat) — never log in cleartext.",
            ),
            sa.Column("contact_name", sa.String(length=255), nullable=True),
            sa.Column(
                "contact_phone",
                sa.String(length=20),
                nullable=True,
                comment="SENSITIVE — never log in cleartext.",
            ),
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
            sa.PrimaryKeyConstraint("id"),
            comment="Hospitals. contact_phone and location are SENSITIVE.",
        )
        op.create_index("ix_hospitals_city", "hospitals", ["city"])

    if not _has_table("urgency_requests"):
        op.create_table(
            "urgency_requests",
            sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
            sa.Column("public_ref", sa.String(length=40), nullable=False),
            sa.Column(
                "blood_group_needed",
                postgresql.ENUM(*BLOOD_GROUP_VALUES, name="blood_group", create_type=False),
                nullable=False,
                comment="SENSITIVE — never log in cleartext.",
            ),
            sa.Column(
                "patient_display_name",
                sa.String(length=255),
                nullable=False,
                comment="Demo-only display name. SENSITIVE — never log in cleartext.",
            ),
            sa.Column("hospital_id", sa.Uuid(), nullable=False),
            sa.Column(
                "status",
                postgresql.ENUM(*URGENCY_STATUS_VALUES, name="urgency_status", create_type=False),
                server_default="open",
                nullable=False,
            ),
            sa.Column("units_needed", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("zone_label", sa.String(length=255), nullable=True),
            sa.Column("alerted_donors_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("confirmed_donations_count", sa.Integer(), nullable=False, server_default="0"),
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
            sa.CheckConstraint("units_needed >= 1", name="ck_urgency_units_needed"),
            sa.CheckConstraint("alerted_donors_count >= 0", name="ck_urgency_alerted_count"),
            sa.CheckConstraint("confirmed_donations_count >= 0", name="ck_urgency_confirmed_count"),
            sa.ForeignKeyConstraint(["hospital_id"], ["hospitals.id"], ondelete="RESTRICT"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("public_ref"),
            comment=(
                "Emergency requests. blood_group_needed and "
                "patient_display_name are SENSITIVE."
            ),
        )
        op.create_index("ix_urgency_requests_status", "urgency_requests", ["status"])
        op.create_index(
            "ix_urgency_requests_blood_group_needed",
            "urgency_requests",
            ["blood_group_needed"],
        )
        op.create_index("ix_urgency_requests_hospital_id", "urgency_requests", ["hospital_id"])

    if not _has_table("donation_confirmations"):
        op.create_table(
            "donation_confirmations",
            sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
            sa.Column("donor_id", sa.Uuid(), nullable=False),
            sa.Column("urgency_request_id", sa.Uuid(), nullable=False),
            sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column(
                "status",
                postgresql.ENUM(*DONATION_STATUS_VALUES, name="donation_status", create_type=False),
                server_default="pending",
                nullable=False,
            ),
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
            sa.ForeignKeyConstraint(["donor_id"], ["donors.id"], ondelete="RESTRICT"),
            sa.ForeignKeyConstraint(
                ["urgency_request_id"],
                ["urgency_requests.id"],
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "donor_id",
                "urgency_request_id",
                name="uq_donation_confirmations_donor_urgency",
            ),
            comment="Donor confirmations against an urgency request.",
        )
        op.create_index("ix_donation_confirmations_donor_id", "donation_confirmations", ["donor_id"])
        op.create_index(
            "ix_donation_confirmations_urgency_request_id",
            "donation_confirmations",
            ["urgency_request_id"],
        )


def downgrade() -> None:
    if _has_table("donation_confirmations"):
        op.drop_index(
            "ix_donation_confirmations_urgency_request_id",
            table_name="donation_confirmations",
        )
        op.drop_index("ix_donation_confirmations_donor_id", table_name="donation_confirmations")
        op.drop_table("donation_confirmations")

    if _has_table("urgency_requests"):
        op.drop_index("ix_urgency_requests_hospital_id", table_name="urgency_requests")
        op.drop_index("ix_urgency_requests_blood_group_needed", table_name="urgency_requests")
        op.drop_index("ix_urgency_requests_status", table_name="urgency_requests")
        op.drop_table("urgency_requests")

    if _has_table("hospitals"):
        op.drop_index("ix_hospitals_city", table_name="hospitals")
        op.drop_table("hospitals")

    if _has_table("donors"):
        op.drop_index("ix_donors_city", table_name="donors")
        op.drop_index("ix_donors_blood_group", table_name="donors")
        op.drop_table("donors")

    postgresql.ENUM(name="donation_status").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="urgency_status").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="blood_group").drop(op.get_bind(), checkfirst=True)
