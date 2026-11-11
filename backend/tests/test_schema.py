"""Unit tests for MVP models and Pydantic schemas (no database)."""

import unittest
from uuid import uuid4

from app.enums import BloodGroup, DonationStatus
from app.models import Base, Donor, Hospital, UrgencyRequest, User
from app.rules import UnrecognizedHospitalError, require_recognized_hospital
from app.schemas import (
    DonationConfirmationCreate,
    DonorCreate,
    HospitalCreate,
    UrgencyRequestCreate,
)


class ModelMetadataTests(unittest.TestCase):
    def test_expected_tables(self) -> None:
        self.assertEqual(
            set(Base.metadata.tables),
            {
                "donors",
                "hospitals",
                "urgency_requests",
                "donation_confirmations",
                "urgency_matches",
                "users",
                "posts",
                "follows",
                "post_likes",
                "post_comments",
                "conversations",
                "conversation_members",
                "direct_messages",
                "communities",
                "community_members",
                "community_rooms",
                "community_messages",
            },
        )

    def test_sensitive_columns_are_marked(self) -> None:
        marked = {
            Donor.__table__.c.phone.comment,
            Donor.__table__.c.blood_group.comment,
            Donor.__table__.c.location.comment,
            Hospital.__table__.c.location.comment,
            Hospital.__table__.c.contact_phone.comment,
            UrgencyRequest.__table__.c.blood_group_needed.comment,
            UrgencyRequest.__table__.c.patient_display_name.comment,
            User.__table__.c.email.comment,
            User.__table__.c.password_hash.comment,
        }
        for comment in marked:
            self.assertIsNotNone(comment)
            self.assertIn("SENSITIVE", comment.upper())

    def test_hospital_is_recognized_defaults_false(self) -> None:
        column = Hospital.__table__.c.is_recognized
        self.assertFalse(column.nullable)
        self.assertEqual(str(column.server_default.arg), "false")

    def test_urgency_uses_hospital_fk_only(self) -> None:
        columns = set(UrgencyRequest.__table__.c.keys())
        self.assertIn("hospital_id", columns)
        self.assertNotIn("hospital_name", columns)
        self.assertNotIn("hospital", columns)


class SchemaTests(unittest.TestCase):
    def test_donor_create_fictional_payload(self) -> None:
        payload = DonorCreate(
            display_name="Donneur Demo",
            blood_group=BloodGroup.O_POSITIVE,
            phone="0190000000",
            city="Zone Demo",
        )
        self.assertEqual(payload.city, "Zone Demo")

    def test_hospital_create_fictional_payload(self) -> None:
        payload = HospitalCreate(name="Hopital Demo", city="Zone Demo")
        self.assertEqual(payload.name, "Hopital Demo")
        self.assertFalse(payload.is_recognized)

    def test_hospital_create_can_mark_recognized(self) -> None:
        payload = HospitalCreate(
            name="Hopital Demo",
            city="Zone Demo",
            is_recognized=True,
        )
        self.assertTrue(payload.is_recognized)

    def test_require_recognized_hospital(self) -> None:
        recognized = Hospital(name="Hopital Demo", city="Zone Demo", is_recognized=True)
        unrecognized = Hospital(
            name="Clinique Demo Non Reconnue",
            city="Zone Demo",
            is_recognized=False,
        )
        require_recognized_hospital(recognized)
        with self.assertRaises(UnrecognizedHospitalError):
            require_recognized_hospital(unrecognized)

    def test_urgency_create_fictional_payload(self) -> None:
        payload = UrgencyRequestCreate(
            public_ref="REQ-DEMO-001",
            blood_group_needed="O+",
            patient_display_name="Patient Demo",
            hospital_id=uuid4(),
            zone_label="Zone Demo",
        )
        self.assertEqual(payload.public_ref, "REQ-DEMO-001")
        self.assertEqual(payload.units_needed, 1)

    def test_donation_create(self) -> None:
        donor_id = uuid4()
        urgency_id = uuid4()
        payload = DonationConfirmationCreate(donor_id=donor_id, urgency_request_id=urgency_id)
        self.assertEqual(payload.donor_id, donor_id)
        self.assertEqual(DonationStatus.PENDING.value, "pending")


if __name__ == "__main__":
    unittest.main()
