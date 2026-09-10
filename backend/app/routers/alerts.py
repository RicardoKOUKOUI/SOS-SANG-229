"""Create an urgency, validate the hospital, run matching, persist candidates."""

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db
from app.enums import UrgencyStatus
from app.matching import find_compatible_donors
from app.models import Hospital, UrgencyMatch, UrgencyRequest
from app.notifications import default_notifier
from app.refs import new_public_ref
from app.rules import UnrecognizedHospitalError, require_recognized_hospital
from app.schemas.urgency import (
    MatchedDonorPublic,
    MatchingSummary,
    NotificationStub,
    UrgencyCreateResponse,
    UrgencyRequestCreate,
)

router = APIRouter(prefix="/alerts", tags=["alerts"])


def _http_unrecognized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=(
            "Urgency requests may only target a state-recognized hospital "
            "(hospitals.is_recognized must be true)."
        ),
    )


@router.post(
    "",
    response_model=UrgencyCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an urgency and match nearby donors",
    description=(
        "Requires a recognized `hospital_id`. Runs GPS/city matching "
        "(GPS within MATCH_RADIUS_METERS, default 15 km, else same city), "
        "stores `alerted_donors_count`, and links candidates without phones. "
        "Twilio is not called."
    ),
)
def create_alert(
    payload: UrgencyRequestCreate,
    db: Session = Depends(get_db),
) -> UrgencyCreateResponse:
    hospital = db.get(Hospital, payload.hospital_id)
    if hospital is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital not found.",
        )
    try:
        require_recognized_hospital(hospital)
    except UnrecognizedHospitalError:
        raise _http_unrecognized() from None

    radius = get_settings().match_radius_meters
    matches = find_compatible_donors(
        db,
        hospital,
        payload.blood_group_needed,
        radius_meters=radius,
    )

    public_ref = payload.public_ref or new_public_ref()
    urgency = UrgencyRequest(
        id=uuid4(),
        public_ref=public_ref,
        blood_group_needed=payload.blood_group_needed,
        patient_display_name=payload.patient_display_name,
        hospital_id=hospital.id,
        status=UrgencyStatus.ALERTING if matches else UrgencyStatus.OPEN,
        units_needed=payload.units_needed,
        zone_label=payload.zone_label,
        alerted_donors_count=len(matches),
        confirmed_donations_count=0,
    )
    db.add(urgency)
    try:
        db.flush()
        for match in matches:
            db.add(
                UrgencyMatch(
                    id=uuid4(),
                    urgency_request_id=urgency.id,
                    donor_id=match.donor.id,
                    match_method=match.method,
                )
            )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        message = str(getattr(exc, "orig", exc)).lower()
        if "is_recognized" in message:
            raise _http_unrecognized() from None
        if "public_ref" in message or "uq" in message:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This public_ref is already in use.",
            ) from None
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not create the urgency request.",
        ) from None

    db.refresh(urgency)
    default_notifier().notify_matched_donors(donor_count=len(matches))

    candidates = [
        MatchedDonorPublic(
            donor_id=match.donor.id,
            display_name=match.donor.display_name,
            city=match.donor.city,
            match_method=match.method,
        )
        for match in matches
    ]
    return UrgencyCreateResponse(
        id=urgency.id,
        public_ref=urgency.public_ref,
        blood_group_needed=urgency.blood_group_needed,
        patient_display_name=urgency.patient_display_name,
        hospital_id=urgency.hospital_id,
        status=urgency.status,
        units_needed=urgency.units_needed,
        zone_label=urgency.zone_label,
        alerted_donors_count=urgency.alerted_donors_count,
        confirmed_donations_count=urgency.confirmed_donations_count,
        created_at=urgency.created_at,
        updated_at=urgency.updated_at,
        hospital_name=hospital.name,
        hospital_city=hospital.city,
        matching=MatchingSummary(
            radius_meters=radius,
            match_count=len(candidates),
            candidates=candidates,
        ),
        notification=NotificationStub(),
    )
