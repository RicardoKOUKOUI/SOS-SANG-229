"""Donor registration. Responses omit phone and GPS."""

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.geo import geopoint_to_wkt
from app.models import Donor
from app.schemas.donor import DonorCreate, DonorPublic

router = APIRouter(prefix="/donors", tags=["donors"])


@router.post(
    "",
    response_model=DonorPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Register a donor",
    description=(
        "Create a donor profile. The response omits phone and GPS."
    ),
)
def create_donor(payload: DonorCreate, db: Session = Depends(get_db)) -> Donor:
    donor = Donor(
        id=uuid4(),
        display_name=payload.display_name,
        blood_group=payload.blood_group,
        phone=payload.phone,
        city=payload.city,
        location=geopoint_to_wkt(payload.location),
        is_available=payload.is_available,
    )
    db.add(donor)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un donneur avec ce numéro est déjà inscrit.",
        ) from None
    db.refresh(donor)
    return donor
