"""Professional, jobs, and marketplace listings. Checkout stays refused."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.deps import get_current_user
from app.models.listings import JobListing, MarketListing, ProfessionalProfile
from app.models.user import User
from app.schemas.listings import (
    JobCreate,
    JobRead,
    MarketCreate,
    MarketRead,
    ProfessionalRead,
    ProfessionalUpsert,
)
from app.schemas.social import AuthorBrief

router = APIRouter(tags=["listings"])


def _pro(profile: ProfessionalProfile) -> ProfessionalRead:
    return ProfessionalRead(
        id=profile.id,
        headline=profile.headline,
        organization=profile.organization,
        city_label=profile.city_label,
        summary=profile.summary,
        user=AuthorBrief.model_validate(profile.user),
    )


def _job(job: JobListing) -> JobRead:
    return JobRead(
        id=job.id,
        title=job.title,
        description=job.description,
        city_label=job.city_label,
        created_at=job.created_at,
        created_by=AuthorBrief.model_validate(job.created_by),
    )


def _market(item: MarketListing) -> MarketRead:
    return MarketRead(
        id=item.id,
        title=item.title,
        description=item.description,
        price_minor=item.price_minor,
        currency=item.currency,
        checkout_available=False,
        created_at=item.created_at,
        created_by=AuthorBrief.model_validate(item.created_by),
    )


@router.get("/professionals", response_model=list[ProfessionalRead])
def list_professionals(db: Session = Depends(get_db)) -> list[ProfessionalRead]:
    rows = db.scalars(
        select(ProfessionalProfile)
        .options(selectinload(ProfessionalProfile.user))
        .order_by(ProfessionalProfile.created_at.desc())
        .limit(100)
    ).all()
    return [_pro(row) for row in rows]


@router.get("/professional/me", response_model=ProfessionalRead)
def get_my_professional(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProfessionalRead:
    profile = db.scalar(
        select(ProfessionalProfile)
        .options(selectinload(ProfessionalProfile.user))
        .where(ProfessionalProfile.user_id == current_user.id)
    )
    if profile is None:
        raise HTTPException(status_code=404, detail="Professional profile not set.")
    return _pro(profile)


@router.put("/professional/me", response_model=ProfessionalRead)
def upsert_professional(
    payload: ProfessionalUpsert,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProfessionalRead:
    if not payload.headline:
        raise HTTPException(status_code=400, detail="Headline required.")
    profile = db.scalar(
        select(ProfessionalProfile).where(ProfessionalProfile.user_id == current_user.id)
    )
    if profile is None:
        profile = ProfessionalProfile(user_id=current_user.id, headline=payload.headline)
        db.add(profile)
    profile.headline = payload.headline
    profile.organization = payload.organization
    profile.city_label = payload.city_label
    profile.summary = payload.summary
    db.commit()
    loaded = db.scalar(
        select(ProfessionalProfile)
        .options(selectinload(ProfessionalProfile.user))
        .where(ProfessionalProfile.user_id == current_user.id)
    )
    assert loaded is not None
    return _pro(loaded)


@router.get("/jobs", response_model=list[JobRead])
def list_jobs(db: Session = Depends(get_db)) -> list[JobRead]:
    rows = db.scalars(
        select(JobListing)
        .options(selectinload(JobListing.created_by))
        .order_by(JobListing.created_at.desc())
        .limit(100)
    ).all()
    return [_job(row) for row in rows]


@router.post("/jobs", response_model=JobRead, status_code=status.HTTP_201_CREATED)
def create_job(
    payload: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobRead:
    if not payload.title:
        raise HTTPException(status_code=400, detail="Title required.")
    job = JobListing(
        title=payload.title,
        description=payload.description,
        city_label=payload.city_label,
        created_by_id=current_user.id,
    )
    db.add(job)
    db.commit()
    loaded = db.scalar(
        select(JobListing)
        .options(selectinload(JobListing.created_by))
        .where(JobListing.id == job.id)
    )
    assert loaded is not None
    return _job(loaded)


@router.get("/jobs/{job_id}", response_model=JobRead)
def get_job(job_id: UUID, db: Session = Depends(get_db)) -> JobRead:
    job = db.scalar(
        select(JobListing)
        .options(selectinload(JobListing.created_by))
        .where(JobListing.id == job_id)
    )
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    return _job(job)


@router.get("/marketplace", response_model=list[MarketRead])
def list_market(db: Session = Depends(get_db)) -> list[MarketRead]:
    rows = db.scalars(
        select(MarketListing)
        .options(selectinload(MarketListing.created_by))
        .order_by(MarketListing.created_at.desc())
        .limit(100)
    ).all()
    return [_market(row) for row in rows]


@router.post("/marketplace", response_model=MarketRead, status_code=status.HTTP_201_CREATED)
def create_listing(
    payload: MarketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MarketRead:
    if not payload.title:
        raise HTTPException(status_code=400, detail="Title required.")
    item = MarketListing(
        title=payload.title,
        description=payload.description,
        price_minor=payload.price_minor,
        currency="XOF",
        created_by_id=current_user.id,
    )
    db.add(item)
    db.commit()
    loaded = db.scalar(
        select(MarketListing)
        .options(selectinload(MarketListing.created_by))
        .where(MarketListing.id == item.id)
    )
    assert loaded is not None
    return _market(loaded)


@router.get("/marketplace/{listing_id}", response_model=MarketRead)
def get_listing(listing_id: UUID, db: Session = Depends(get_db)) -> MarketRead:
    item = db.scalar(
        select(MarketListing)
        .options(selectinload(MarketListing.created_by))
        .where(MarketListing.id == listing_id)
    )
    if item is None:
        raise HTTPException(status_code=404, detail="Listing not found.")
    return _market(item)


@router.post("/marketplace/{listing_id}/checkout", status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
def checkout_listing(
    listing_id: UUID,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> None:
    item = db.get(MarketListing, listing_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Listing not found.")
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=(
            "Pay is not active. The listing price is display-only; "
            "no charge was made."
        ),
    )
