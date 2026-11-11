"""HUB Events (DB-only)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.deps import get_current_user, get_optional_user
from app.models.hub import Event
from app.models.user import User
from app.schemas.hub import EventCreate, EventRead
from app.schemas.social import AuthorBrief

router = APIRouter(prefix="/events", tags=["events"])


def _read(event: Event) -> EventRead:
    return EventRead(
        id=event.id,
        title=event.title,
        description=event.description,
        location_label=event.location_label,
        starts_at=event.starts_at,
        ends_at=event.ends_at,
        created_by=AuthorBrief.model_validate(event.created_by),
    )


@router.get("", response_model=list[EventRead])
def list_events(
    db: Session = Depends(get_db),
    _viewer: User | None = Depends(get_optional_user),
) -> list[EventRead]:
    events = db.scalars(
        select(Event)
        .options(selectinload(Event.created_by))
        .order_by(Event.starts_at.asc())
        .limit(100)
    ).all()
    return [_read(event) for event in events]


@router.post("", response_model=EventRead, status_code=status.HTTP_201_CREATED)
def create_event(
    payload: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EventRead:
    if payload.ends_at and payload.ends_at < payload.starts_at:
        raise HTTPException(status_code=400, detail="ends_at must be after starts_at.")
    event = Event(
        title=payload.title,
        description=payload.description,
        location_label=payload.location_label,
        starts_at=payload.starts_at,
        ends_at=payload.ends_at,
        created_by_id=current_user.id,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    event = db.scalar(
        select(Event).options(selectinload(Event.created_by)).where(Event.id == event.id)
    )
    assert event is not None
    return _read(event)


@router.get("/{event_id}", response_model=EventRead)
def get_event(event_id: UUID, db: Session = Depends(get_db)) -> EventRead:
    event = db.scalar(
        select(Event).options(selectinload(Event.created_by)).where(Event.id == event_id)
    )
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found.")
    return _read(event)
