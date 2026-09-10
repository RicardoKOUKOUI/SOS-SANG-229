"""Insert clearly fictional demo rows.

Never logs phone numbers, GPS coordinates, or blood groups.
Hospitals: recognized Benin facilities from app.data.benin_hospitals
(usable for urgencies) plus one unrecognized demo clinic.
Re-running upserts hospital flags/names and skips existing urgency rows.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import select  # noqa: E402

from app.data.benin_hospitals import BENIN_HOSPITALS  # noqa: E402
from app.db import get_session_factory  # noqa: E402
from app.enums import BloodGroup, DonationStatus, MatchMethod, UrgencyStatus  # noqa: E402
from app.models import (  # noqa: E402
    DonationConfirmation,
    Donor,
    Hospital,
    UrgencyMatch,
    UrgencyRequest,
)
from app.rules import require_recognized_hospital  # noqa: E402

# Approximate public facility centroids (WGS84). Do not print.
def _pt(lon: float, lat: float) -> str:
    return f"POINT({lon} {lat})"


RECOGNIZED_HOSPITAL_ID = UUID("00000000-0000-4000-8000-000000000010")
UNRECOGNIZED_HOSPITAL_ID = UUID("00000000-0000-4000-8000-000000000011")
DONOR_ID = UUID("00000000-0000-4000-8000-000000000001")
URGENCY_ID = UUID("00000000-0000-4000-8000-000000000020")
MATCH_ID = UUID("00000000-0000-4000-8000-000000000021")
CONFIRM_ID = UUID("00000000-0000-4000-8000-000000000030")
# Backward-compatible alias used by earlier seed revisions.
HOSPITAL_ID = RECOGNIZED_HOSPITAL_ID


def _upsert_hospital(
    session,
    hospital_id: UUID,
    *,
    name: str,
    city: str,
    location: str | None,
    is_recognized: bool,
    contact_name: str | None = "Contact Demo",
    contact_phone: str | None = "+22900000099",
) -> Hospital:
    hospital = session.get(Hospital, hospital_id)
    if hospital is None:
        hospital = Hospital(
            id=hospital_id,
            name=name,
            city=city,
            location=location,
            contact_name=contact_name,
            contact_phone=contact_phone,
            is_recognized=is_recognized,
        )
        session.add(hospital)
        return hospital
    hospital.name = name
    hospital.city = city
    if location is not None:
        hospital.location = location
    hospital.is_recognized = is_recognized
    return hospital


def main() -> None:
    session = get_session_factory()()
    try:
        recognized_rows: list[Hospital] = []
        for entry in BENIN_HOSPITALS:
            row = _upsert_hospital(
                session,
                entry["id"],
                name=entry["name"],
                city=entry["city"],
                location=_pt(entry["lon"], entry["lat"]),
                is_recognized=True,
            )
            recognized_rows.append(row)

        _upsert_hospital(
            session,
            UNRECOGNIZED_HOSPITAL_ID,
            name="Clinique Demo Non Reconnue",
            city="Cotonou",
            location=_pt(2.42, 6.37),
            is_recognized=False,
        )

        primary = next(
            (r for r in recognized_rows if r.id == RECOGNIZED_HOSPITAL_ID),
            recognized_rows[0],
        )
        require_recognized_hospital(primary)

        already = session.scalar(
            select(UrgencyRequest.id).where(UrgencyRequest.public_ref == "REQ-DEMO-001")
        )
        if already is not None:
            # Keep demo urgency pointed at the primary recognized hospital.
            urgency = session.get(UrgencyRequest, URGENCY_ID)
            if urgency is not None:
                urgency.hospital_id = RECOGNIZED_HOSPITAL_ID
                urgency.zone_label = "Cotonou — Akpakpa"
            session.commit()
            print(
                f"Demo seed refreshed: {len(BENIN_HOSPITALS)} recognized hospitals, "
                "REQ-DEMO-001 already present. Sensitive fields are not printed."
            )
            return

        donor = session.get(Donor, DONOR_ID)
        if donor is None:
            session.add(
                Donor(
                    id=DONOR_ID,
                    display_name="Donneur Demo",
                    blood_group=BloodGroup.O_POSITIVE,
                    phone="0190000001",
                    city="Cotonou",
                    location=_pt(2.43, 6.36),
                    is_available=True,
                )
            )
        else:
            # Ensure demo donor uses Benin 01… national format.
            if not str(donor.phone or "").startswith("01"):
                donor.phone = "0190000001"

        session.add(
            UrgencyRequest(
                id=URGENCY_ID,
                public_ref="REQ-DEMO-001",
                blood_group_needed=BloodGroup.O_POSITIVE,
                patient_display_name="Patient Demo",
                hospital_id=RECOGNIZED_HOSPITAL_ID,
                status=UrgencyStatus.ALERTING,
                units_needed=1,
                zone_label="Cotonou — Akpakpa",
                alerted_donors_count=1,
                confirmed_donations_count=1,
            )
        )
        session.add(
            UrgencyMatch(
                id=MATCH_ID,
                urgency_request_id=URGENCY_ID,
                donor_id=DONOR_ID,
                match_method=MatchMethod.GPS,
            )
        )
        session.add(
            DonationConfirmation(
                id=CONFIRM_ID,
                donor_id=DONOR_ID,
                urgency_request_id=URGENCY_ID,
                status=DonationStatus.CONFIRMED,
                confirmed_at=datetime.now(timezone.utc),
            )
        )
        session.commit()
        print(
            f"Inserted fictional demo rows "
            f"({len(BENIN_HOSPITALS)} recognized Benin hospitals, "
            "Clinique Demo Non Reconnue, Donneur Demo, REQ-DEMO-001). "
            "Sensitive fields are not printed."
        )
    finally:
        session.close()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback

        traceback.print_exc()
        raise
