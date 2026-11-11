"""API tests with fictional data only. Phone/GPS are never asserted in cleartext."""

from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.enums import BloodGroup
from app.models import Donor, Hospital
from app.rules import UnrecognizedHospitalError, require_recognized_hospital


def _recognized_hospital(db: Session, city: str = "Zone Demo") -> Hospital:
    hospital = Hospital(
        id=uuid4(),
        name="Hopital Demo",
        city=city,
        is_recognized=True,
    )
    db.add(hospital)
    db.commit()
    db.refresh(hospital)
    return hospital


def _unrecognized_hospital(db: Session) -> Hospital:
    hospital = Hospital(
        id=uuid4(),
        name="Clinique Demo Non Reconnue",
        city="Zone Demo",
        is_recognized=False,
    )
    db.add(hospital)
    db.commit()
    db.refresh(hospital)
    return hospital


def _donor(
    db: Session,
    *,
    city: str = "Zone Demo",
    blood_group: BloodGroup = BloodGroup.O_POSITIVE,
    available: bool = True,
    phone: str = "0190000000",
    name: str = "Donneur Demo",
) -> Donor:
    donor = Donor(
        id=uuid4(),
        display_name=name,
        blood_group=blood_group,
        phone=phone,
        city=city,
        location=None,
        is_available=available,
    )
    db.add(donor)
    db.commit()
    db.refresh(donor)
    return donor


def test_health_ok(api_client: TestClient) -> None:
    response = api_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_openapi_lists_business_paths(api_client: TestClient) -> None:
    spec = api_client.get("/openapi.json").json()
    paths = spec["paths"]
    assert "/health" in paths
    assert "/hospitals" in paths
    assert "/hospitals/recognized" in paths
    assert "/donors" in paths
    assert "/alerts" in paths
    assert "/donations" in paths
    assert "/requests/{public_ref}" in paths
    assert "phone" not in spec["components"]["schemas"]["HospitalPublic"]["properties"]
    assert "phone" not in spec["components"]["schemas"]["DonorPublic"]["properties"]
    assert "phone" not in spec["components"]["schemas"]["UrgencyTrackingRead"]["properties"]


def test_list_recognized_hospitals_omits_unrecognized(
    client: TestClient,
    db_session: Session,
) -> None:
    recognized = _recognized_hospital(db_session)
    _unrecognized_hospital(db_session)

    response = client.get("/hospitals/recognized")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == str(recognized.id)
    assert body[0]["name"] == "Hopital Demo"
    assert "contact_phone" not in body[0]
    assert "location" not in body[0]
    assert "phone" not in body[0]


def test_register_donor_omits_phone(client: TestClient) -> None:
    response = client.post(
        "/donors",
        json={
            "display_name": "Donneur Demo",
            "blood_group": "O+",
            "phone": "0190000000",
            "city": "Zone Demo",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["display_name"] == "Donneur Demo"
    assert body["city"] == "Zone Demo"
    assert "phone" not in body
    assert "location" not in body


def test_register_donor_duplicate_phone_conflict(
    client: TestClient,
    db_session: Session,
) -> None:
    _donor(db_session, phone="0190000000")
    response = client.post(
        "/donors",
        json={
            "display_name": "Donneur Demo 2",
            "blood_group": "A+",
            "phone": "0190000000",
            "city": "Zone Demo",
        },
    )
    assert response.status_code == 409
    assert "+229" not in response.text


def test_create_urgency_rejects_unrecognized_hospital(
    client: TestClient,
    db_session: Session,
) -> None:
    hospital = _unrecognized_hospital(db_session)
    response = client.post(
        "/alerts",
        json={
            "public_ref": "REQ-DEMO-UNREC",
            "blood_group_needed": "O+",
            "patient_display_name": "Patient Demo",
            "hospital_id": str(hospital.id),
        },
    )
    assert response.status_code == 400
    assert "recognized" in response.json()["detail"].lower()


def test_create_urgency_rejects_missing_hospital(client: TestClient) -> None:
    response = client.post(
        "/alerts",
        json={
            "blood_group_needed": "O+",
            "patient_display_name": "Patient Demo",
            "hospital_id": str(uuid4()),
        },
    )
    assert response.status_code == 404


def test_create_urgency_duplicate_public_ref_conflict(
    client: TestClient,
    db_session: Session,
) -> None:
    hospital = _recognized_hospital(db_session)
    payload = {
        "public_ref": "REQ-DEMO-DUP",
        "blood_group_needed": "O+",
        "patient_display_name": "Patient Demo",
        "hospital_id": str(hospital.id),
    }
    first = client.post("/alerts", json=payload)
    assert first.status_code == 201
    second = client.post("/alerts", json=payload)
    assert second.status_code == 409
    assert "public_ref" in second.json()["detail"].lower()
    assert "+229" not in second.text


def test_create_urgency_matches_compatible_city_donor(
    client: TestClient,
    db_session: Session,
) -> None:
    hospital = _recognized_hospital(db_session, city="Zone Demo")
    nearby = _donor(
        db_session,
        city="Zone Demo",
        blood_group=BloodGroup.O_NEGATIVE,
        phone="0190000001",
        name="Donneur Demo Compatible",
    )
    _donor(
        db_session,
        city="Ville Demo",
        blood_group=BloodGroup.O_NEGATIVE,
        phone="0190000002",
        name="Donneur Demo Loin",
    )
    _donor(
        db_session,
        city="Zone Demo",
        blood_group=BloodGroup.A_POSITIVE,
        phone="0190000003",
        name="Donneur Demo Incompatible",
    )
    _donor(
        db_session,
        city="Zone Demo",
        blood_group=BloodGroup.O_NEGATIVE,
        phone="0190000004",
        name="Donneur Demo Indisponible",
        available=False,
    )

    response = client.post(
        "/alerts",
        json={
            "public_ref": "REQ-DEMO-MATCH",
            "blood_group_needed": "O+",
            "patient_display_name": "Patient Demo",
            "hospital_id": str(hospital.id),
            "zone_label": "Zone Demo",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["public_ref"] == "REQ-DEMO-MATCH"
    assert body["alerted_donors_count"] == 1
    assert body["status"] == "alerting"
    assert body["matching"]["radius_meters"] == 15_000
    assert body["matching"]["match_count"] == 1
    assert body["matching"]["candidates"][0]["donor_id"] == str(nearby.id)
    assert body["matching"]["candidates"][0]["match_method"] == "city"
    assert "phone" not in body["matching"]["candidates"][0]
    assert body["notification"]["sent"] is False
    assert "+229" not in response.text


def test_tracking_and_confirm_donation(
    client: TestClient,
    db_session: Session,
) -> None:
    hospital = _recognized_hospital(db_session)
    donor = _donor(db_session)

    created = client.post(
        "/alerts",
        json={
            "public_ref": "REQ-DEMO-TRACK",
            "blood_group_needed": "O+",
            "patient_display_name": "Patient Demo",
            "hospital_id": str(hospital.id),
        },
    )
    assert created.status_code == 201
    urgency_id = created.json()["id"]

    tracking = client.get("/requests/REQ-DEMO-TRACK")
    assert tracking.status_code == 200
    track_body = tracking.json()
    assert track_body["alerted_donors_count"] == 1
    assert track_body["confirmed_donations_count"] == 0
    assert track_body["status"] == "alerting"
    assert "phone" not in track_body
    assert all("phone" not in item for item in track_body["matched_donors"])

    listed = client.get("/requests")
    assert listed.status_code == 200
    assert listed.json()[0]["public_ref"] == "REQ-DEMO-TRACK"
    assert "phone" not in listed.json()[0]
    assert "blood_group_needed" not in listed.json()[0]

    confirm = client.post(
        "/donations",
        json={"donor_id": str(donor.id), "urgency_request_id": urgency_id},
    )
    assert confirm.status_code == 201
    assert confirm.json()["status"] == "confirmed"
    assert "phone" not in confirm.json()

    after = client.get("/requests/REQ-DEMO-TRACK")
    assert after.json()["confirmed_donations_count"] == 1
    assert after.json()["status"] == "fulfilled"

    duplicate = client.post(
        "/donations",
        json={"donor_id": str(donor.id), "urgency_request_id": urgency_id},
    )
    assert duplicate.status_code == 409


def test_create_urgency_matches_gps_donor_inside_radius(
    client: TestClient,
    db_session: Session,
) -> None:
    from app.geo import geopoint_to_wkt
    from app.schemas.common import GeoPoint

    hospital = Hospital(
        id=uuid4(),
        name="Hopital Demo",
        city="Zone Demo",
        is_recognized=True,
        location=geopoint_to_wkt(GeoPoint(latitude=6.37, longitude=2.42)),
    )
    db_session.add(hospital)
    nearby = Donor(
        id=uuid4(),
        display_name="Donneur Demo Proche",
        blood_group=BloodGroup.O_NEGATIVE,
        phone="0190000011",
        city="Autre Ville Demo",
        location=geopoint_to_wkt(GeoPoint(latitude=6.38, longitude=2.42)),
        is_available=True,
    )
    far = Donor(
        id=uuid4(),
        display_name="Donneur Demo Loin",
        blood_group=BloodGroup.O_NEGATIVE,
        phone="0190000012",
        city="Zone Demo",
        location=geopoint_to_wkt(GeoPoint(latitude=6.60, longitude=2.42)),
        is_available=True,
    )
    db_session.add_all([nearby, far])
    db_session.commit()

    response = client.post(
        "/alerts",
        json={
            "public_ref": "REQ-DEMO-GPS",
            "blood_group_needed": "O+",
            "patient_display_name": "Patient Demo",
            "hospital_id": str(hospital.id),
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["alerted_donors_count"] == 1
    assert body["matching"]["candidates"][0]["donor_id"] == str(nearby.id)
    assert body["matching"]["candidates"][0]["match_method"] == "gps"
    assert "phone" not in body["matching"]["candidates"][0]
    assert "+229" not in response.text


def test_require_recognized_hospital_helper() -> None:
    recognized = Hospital(name="Hopital Demo", city="Zone Demo", is_recognized=True)
    unrecognized = Hospital(
        name="Clinique Demo Non Reconnue",
        city="Zone Demo",
        is_recognized=False,
    )
    require_recognized_hospital(recognized)
    try:
        require_recognized_hospital(unrecognized)
    except UnrecognizedHospitalError:
        return
    raise AssertionError("unrecognized hospital must be rejected")
