"""Creator studio (light) and honest monetization flags. No payouts without a PSP."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.config import get_settings
from app.db import get_db
from app.deps import get_current_user
from app.models.creator import CreatorProfile, FeatureFlag
from app.models.user import User
from app.schemas.creator import (
    CreatorProfileRead,
    CreatorProfileUpsert,
    MonetizationStatusRead,
    PremiumPlanRead,
)
from app.schemas.social import AuthorBrief

router = APIRouter(tags=["creator"])

_PLANS = (
    PremiumPlanRead(
        code="plus",
        name="DOXAMI Plus",
        checkout_available=False,
        note="Catalogue only — checkout requires a payment provider.",
    ),
)


def _flag(db: Session, key: str) -> bool:
    row = db.get(FeatureFlag, key)
    return bool(row and row.enabled)


def _read_profile(profile: CreatorProfile) -> CreatorProfileRead:
    return CreatorProfileRead(
        id=profile.id,
        pitch=profile.pitch,
        focus=profile.focus,
        accepting_collabs=profile.accepting_collabs,
        user=AuthorBrief.model_validate(profile.user),
    )


def _status(db: Session) -> MonetizationStatusRead:
    settings = get_settings()
    psp_configured = bool(settings.doxami_psp_api_key.strip())
    ads = _flag(db, "ads_enabled")
    premium = _flag(db, "premium_enabled")
    # No PSP adapter is shipped in this phase, so payouts stay unavailable
    # even when a key is present. Earnings stay 0: there is no revenue ledger.
    if not psp_configured:
        reason = (
            "DOXAMI_PSP_API_KEY is empty. Ads/Premium flags default off. "
            "No checkout and no payout (balance is 0 — no revenue ledger)."
        )
    else:
        reason = (
            "A PSP key is set, but no payment adapter is implemented. "
            "Checkout and payouts stay unavailable. Balance is 0."
        )
    return MonetizationStatusRead(
        ads_enabled=ads,
        premium_enabled=premium,
        psp_configured=psp_configured,
        payouts_ready=False,
        earnings_minor=0,
        currency="XOF",
        reason=reason,
    )


@router.get("/creator/me", response_model=CreatorProfileRead)
def get_my_creator(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CreatorProfileRead:
    profile = db.scalar(
        select(CreatorProfile)
        .options(selectinload(CreatorProfile.user))
        .where(CreatorProfile.user_id == current_user.id)
    )
    if profile is None:
        raise HTTPException(status_code=404, detail="Creator profile not set.")
    return _read_profile(profile)


@router.put("/creator/me", response_model=CreatorProfileRead)
def upsert_my_creator(
    payload: CreatorProfileUpsert,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CreatorProfileRead:
    profile = db.scalar(
        select(CreatorProfile).where(CreatorProfile.user_id == current_user.id)
    )
    if profile is None:
        profile = CreatorProfile(user_id=current_user.id)
        db.add(profile)
    profile.pitch = payload.pitch
    profile.focus = payload.focus
    profile.accepting_collabs = payload.accepting_collabs
    db.commit()
    loaded = db.scalar(
        select(CreatorProfile)
        .options(selectinload(CreatorProfile.user))
        .where(CreatorProfile.user_id == current_user.id)
    )
    assert loaded is not None
    return _read_profile(loaded)


@router.get("/monetization/status", response_model=MonetizationStatusRead)
def monetization_status(db: Session = Depends(get_db)) -> MonetizationStatusRead:
    return _status(db)


@router.get("/monetization/plans", response_model=list[PremiumPlanRead])
def list_plans() -> list[PremiumPlanRead]:
    return list(_PLANS)


@router.post("/monetization/checkout", status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
def checkout(_current_user: User = Depends(get_current_user)) -> None:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=(
            "Premium checkout is not available. "
            "No payment provider adapter is configured."
        ),
    )


@router.post("/creator/payouts", status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
def request_payout(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> None:
    status_read = _status(db)
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=(
            "Payouts are not available. "
            f"payouts_ready={status_read.payouts_ready}, "
            f"earnings_minor={status_read.earnings_minor}. "
            "No PSP adapter and no revenue ledger."
        ),
    )
