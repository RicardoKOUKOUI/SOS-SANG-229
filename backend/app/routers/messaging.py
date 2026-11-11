"""Direct + group text messaging (polling, no WebRTC)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.deps import get_current_user
from app.models.messaging import Conversation, ConversationMember, DirectMessage
from app.models.user import User
from app.schemas.messaging import (
    DirectThreadCreate,
    GroupThreadCreate,
    MessageCreate,
    MessageRead,
    ThreadRead,
)
from app.schemas.social import AuthorBrief

router = APIRouter(prefix="/messages", tags=["messages"])


def _require_member(db: Session, conversation_id: UUID, user_id: UUID) -> Conversation:
    conversation = db.scalar(
        select(Conversation)
        .options(
            selectinload(Conversation.members).selectinload(ConversationMember.user),
        )
        .where(Conversation.id == conversation_id)
    )
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found.")
    if not any(member.user_id == user_id for member in conversation.members):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a thread member.")
    return conversation


def _message_read(message: DirectMessage) -> MessageRead:
    return MessageRead(
        id=message.id,
        body=message.body,
        created_at=message.created_at,
        sender=AuthorBrief.model_validate(message.sender),
    )


def _thread_read(db: Session, conversation: Conversation) -> ThreadRead:
    last = db.scalar(
        select(DirectMessage)
        .options(selectinload(DirectMessage.sender))
        .where(DirectMessage.conversation_id == conversation.id)
        .order_by(DirectMessage.created_at.desc())
        .limit(1)
    )
    return ThreadRead(
        id=conversation.id,
        kind=conversation.kind,
        title=conversation.title,
        members=[AuthorBrief.model_validate(member.user) for member in conversation.members],
        last_message=_message_read(last) if last else None,
    )


def _get_user_by_username(db: Session, username: str) -> User:
    user = db.scalar(select(User).where(User.username == username.lower(), User.is_active.is_(True)))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user


@router.get("/threads", response_model=list[ThreadRead])
def list_threads(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ThreadRead]:
    memberships = db.scalars(
        select(ConversationMember.conversation_id).where(
            ConversationMember.user_id == current_user.id
        )
    ).all()
    if not memberships:
        return []
    conversations = db.scalars(
        select(Conversation)
        .options(selectinload(Conversation.members).selectinload(ConversationMember.user))
        .where(Conversation.id.in_(memberships))
        .order_by(Conversation.updated_at.desc())
    ).all()
    return [_thread_read(db, conversation) for conversation in conversations]


@router.post("/threads/direct", response_model=ThreadRead, status_code=status.HTTP_201_CREATED)
def create_or_get_direct(
    payload: DirectThreadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ThreadRead:
    other = _get_user_by_username(db, payload.username)
    if other.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot message yourself.")

    # Find existing 1:1 with exactly these two members.
    my_threads = db.scalars(
        select(Conversation)
        .options(selectinload(Conversation.members).selectinload(ConversationMember.user))
        .join(ConversationMember)
        .where(
            Conversation.kind == "direct",
            ConversationMember.user_id == current_user.id,
        )
    ).all()
    for conversation in my_threads:
        member_ids = {member.user_id for member in conversation.members}
        if member_ids == {current_user.id, other.id}:
            return _thread_read(db, conversation)

    conversation = Conversation(kind="direct", title=None)
    db.add(conversation)
    db.flush()
    db.add(ConversationMember(conversation_id=conversation.id, user_id=current_user.id))
    db.add(ConversationMember(conversation_id=conversation.id, user_id=other.id))
    db.commit()
    conversation = _require_member(db, conversation.id, current_user.id)
    return _thread_read(db, conversation)


@router.post("/threads/group", response_model=ThreadRead, status_code=status.HTTP_201_CREATED)
def create_group(
    payload: GroupThreadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ThreadRead:
    member_ids = {current_user.id}
    for username in payload.usernames:
        member_ids.add(_get_user_by_username(db, username).id)
    conversation = Conversation(kind="group", title=payload.title)
    db.add(conversation)
    db.flush()
    for user_id in member_ids:
        db.add(ConversationMember(conversation_id=conversation.id, user_id=user_id))
    db.commit()
    conversation = _require_member(db, conversation.id, current_user.id)
    return _thread_read(db, conversation)


@router.get("/threads/{thread_id}", response_model=ThreadRead)
def get_thread(
    thread_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ThreadRead:
    conversation = _require_member(db, thread_id, current_user.id)
    return _thread_read(db, conversation)


@router.get("/threads/{thread_id}/messages", response_model=list[MessageRead])
def list_messages(
    thread_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[MessageRead]:
    _require_member(db, thread_id, current_user.id)
    messages = db.scalars(
        select(DirectMessage)
        .options(selectinload(DirectMessage.sender))
        .where(DirectMessage.conversation_id == thread_id)
        .order_by(DirectMessage.created_at.asc())
        .limit(200)
    ).all()
    return [_message_read(message) for message in messages]


@router.post(
    "/threads/{thread_id}/messages",
    response_model=MessageRead,
    status_code=status.HTTP_201_CREATED,
)
def send_message(
    thread_id: UUID,
    payload: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageRead:
    conversation = _require_member(db, thread_id, current_user.id)
    message = DirectMessage(
        conversation_id=conversation.id,
        sender_id=current_user.id,
        body=payload.body,
    )
    db.add(message)
    db.flush()
    conversation.updated_at = message.created_at
    db.add(conversation)
    db.commit()
    db.refresh(message)
    message = db.scalar(
        select(DirectMessage)
        .options(selectinload(DirectMessage.sender))
        .where(DirectMessage.id == message.id)
    )
    assert message is not None
    return _message_read(message)
