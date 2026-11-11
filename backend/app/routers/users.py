"""User profile routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.auth import ProfilePublic, ProfileUpdateRequest, UserPublic

router = APIRouter(tags=["users"])


@router.patch("/users/me", response_model=UserPublic)
def update_me(
    payload: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update.",
        )
    if "display_name" in data and data["display_name"] is not None:
        current_user.display_name = data["display_name"]
    if "bio" in data:
        current_user.bio = data["bio"]
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/users/{username}", response_model=ProfilePublic)
def get_public_profile(username: str, db: Session = Depends(get_db)) -> User:
    user = db.scalar(select(User).where(User.username == username.lower()))
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )
    return user
