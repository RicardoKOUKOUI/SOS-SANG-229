"""Basic communities + text rooms."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.deps import get_current_user, get_optional_user
from app.models.messaging import (
    Community,
    CommunityMember,
    CommunityMessage,
    CommunityRoom,
)
from app.models.user import User
from app.schemas.messaging import (
    CommunityCreate,
    CommunityMessageRead,
    CommunityRead,
    MessageCreate,
    RoomCreate,
    RoomRead,
)
from app.schemas.social import AuthorBrief, FollowRead

router = APIRouter(prefix="/communities", tags=["communities"])


def _community_read(
    db: Session,
    community: Community,
    viewer: User | None,
) -> CommunityRead:
    member_count = db.scalar(
        select(func.count())
        .select_from(CommunityMember)
        .where(CommunityMember.community_id == community.id)
    ) or 0
    is_member = False
    if viewer is not None:
        is_member = (
            db.scalar(
                select(CommunityMember.id).where(
                    CommunityMember.community_id == community.id,
                    CommunityMember.user_id == viewer.id,
                )
            )
            is not None
        )
    return CommunityRead(
        id=community.id,
        name=community.name,
        slug=community.slug,
        description=community.description,
        is_public=community.is_public,
        owner=AuthorBrief.model_validate(community.owner),
        member_count=int(member_count),
        is_member=is_member,
    )


def _get_community(db: Session, community_id: UUID) -> Community:
    community = db.scalar(
        select(Community)
        .options(selectinload(Community.owner))
        .where(Community.id == community_id)
    )
    if community is None:
        raise HTTPException(status_code=404, detail="Community not found.")
    return community


def _require_membership(db: Session, community_id: UUID, user_id: UUID) -> CommunityMember:
    membership = db.scalar(
        select(CommunityMember).where(
            CommunityMember.community_id == community_id,
            CommunityMember.user_id == user_id,
        )
    )
    if membership is None:
        raise HTTPException(status_code=403, detail="Join the community first.")
    return membership


@router.get("", response_model=list[CommunityRead])
def list_communities(
    db: Session = Depends(get_db),
    viewer: User | None = Depends(get_optional_user),
) -> list[CommunityRead]:
    communities = db.scalars(
        select(Community)
        .options(selectinload(Community.owner))
        .where(Community.is_public.is_(True))
        .order_by(Community.created_at.desc())
        .limit(50)
    ).all()
    return [_community_read(db, community, viewer) for community in communities]


@router.post("", response_model=CommunityRead, status_code=status.HTTP_201_CREATED)
def create_community(
    payload: CommunityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CommunityRead:
    community = Community(
        name=payload.name,
        slug=payload.slug,
        description=payload.description,
        is_public=payload.is_public,
        owner_id=current_user.id,
    )
    db.add(community)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Slug already taken.") from exc
    db.add(
        CommunityMember(
            community_id=community.id,
            user_id=current_user.id,
            role="owner",
        )
    )
    db.add(
        CommunityRoom(
            community_id=community.id,
            name="Général",
            slug="general",
        )
    )
    db.commit()
    community = _get_community(db, community.id)
    return _community_read(db, community, current_user)


@router.get("/{community_id}", response_model=CommunityRead)
def get_community(
    community_id: UUID,
    db: Session = Depends(get_db),
    viewer: User | None = Depends(get_optional_user),
) -> CommunityRead:
    community = _get_community(db, community_id)
    if not community.is_public:
        if viewer is None:
            raise HTTPException(status_code=404, detail="Community not found.")
        _require_membership(db, community_id, viewer.id)
    return _community_read(db, community, viewer)


@router.post("/{community_id}/join", status_code=status.HTTP_204_NO_CONTENT)
def join_community(
    community_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    community = _get_community(db, community_id)
    if not community.is_public:
        raise HTTPException(status_code=403, detail="Community is private.")
    existing = db.scalar(
        select(CommunityMember).where(
            CommunityMember.community_id == community_id,
            CommunityMember.user_id == current_user.id,
        )
    )
    if existing is None:
        db.add(
            CommunityMember(
                community_id=community_id,
                user_id=current_user.id,
                role="member",
            )
        )
        db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{community_id}/members", response_model=list[FollowRead])
def list_members(community_id: UUID, db: Session = Depends(get_db)) -> list[FollowRead]:
    community = _get_community(db, community_id)
    if not community.is_public:
        raise HTTPException(status_code=403, detail="Community is private.")
    rows = db.scalars(
        select(CommunityMember)
        .options(selectinload(CommunityMember.user))
        .where(CommunityMember.community_id == community_id)
        .order_by(CommunityMember.created_at.asc())
    ).all()
    return [FollowRead(user=AuthorBrief.model_validate(row.user)) for row in rows]


@router.get("/{community_id}/rooms", response_model=list[RoomRead])
def list_rooms(
    community_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[RoomRead]:
    _require_membership(db, community_id, current_user.id)
    rooms = db.scalars(
        select(CommunityRoom)
        .where(CommunityRoom.community_id == community_id)
        .order_by(CommunityRoom.created_at.asc())
    ).all()
    return [RoomRead.model_validate(room) for room in rooms]


@router.post(
    "/{community_id}/rooms",
    response_model=RoomRead,
    status_code=status.HTTP_201_CREATED,
)
def create_room(
    community_id: UUID,
    payload: RoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RoomRead:
    membership = _require_membership(db, community_id, current_user.id)
    if membership.role not in {"owner", "admin"}:
        raise HTTPException(status_code=403, detail="Only owners/admins can create rooms.")
    room = CommunityRoom(
        community_id=community_id,
        name=payload.name.strip(),
        slug=payload.slug,
    )
    db.add(room)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Room slug already exists.") from exc
    db.refresh(room)
    return RoomRead.model_validate(room)


@router.get(
    "/{community_id}/rooms/{room_id}/messages",
    response_model=list[CommunityMessageRead],
)
def list_room_messages(
    community_id: UUID,
    room_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[CommunityMessageRead]:
    _require_membership(db, community_id, current_user.id)
    room = db.scalar(
        select(CommunityRoom).where(
            CommunityRoom.id == room_id,
            CommunityRoom.community_id == community_id,
        )
    )
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found.")
    messages = db.scalars(
        select(CommunityMessage)
        .options(selectinload(CommunityMessage.author))
        .where(CommunityMessage.room_id == room_id)
        .order_by(CommunityMessage.created_at.asc())
        .limit(200)
    ).all()
    return [
        CommunityMessageRead(
            id=message.id,
            body=message.body,
            created_at=message.created_at,
            author=AuthorBrief.model_validate(message.author),
        )
        for message in messages
    ]


@router.post(
    "/{community_id}/rooms/{room_id}/messages",
    response_model=CommunityMessageRead,
    status_code=status.HTTP_201_CREATED,
)
def post_room_message(
    community_id: UUID,
    room_id: UUID,
    payload: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CommunityMessageRead:
    _require_membership(db, community_id, current_user.id)
    room = db.scalar(
        select(CommunityRoom).where(
            CommunityRoom.id == room_id,
            CommunityRoom.community_id == community_id,
        )
    )
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found.")
    message = CommunityMessage(
        room_id=room_id,
        author_id=current_user.id,
        body=payload.body,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    message = db.scalar(
        select(CommunityMessage)
        .options(selectinload(CommunityMessage.author))
        .where(CommunityMessage.id == message.id)
    )
    assert message is not None
    return CommunityMessageRead(
        id=message.id,
        body=message.body,
        created_at=message.created_at,
        author=AuthorBrief.model_validate(message.author),
    )
