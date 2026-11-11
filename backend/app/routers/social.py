"""Follow graph and explore search."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.deps import get_current_user, get_optional_user
from app.models.social import Follow, Post
from app.models.user import User
from app.routers.posts import _post_read
from app.schemas.social import AuthorBrief, ExploreResults, FollowRead, PostRead

router = APIRouter(tags=["social"])


def _get_active_user(db: Session, username: str) -> User:
    user = db.scalar(select(User).where(User.username == username.lower()))
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user


@router.post("/users/{username}/follow", status_code=status.HTTP_204_NO_CONTENT)
def follow_user(
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    target = _get_active_user(db, username)
    if target.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot follow yourself.",
        )
    existing = db.scalar(
        select(Follow).where(
            Follow.follower_id == current_user.id,
            Follow.following_id == target.id,
        )
    )
    if existing is None:
        db.add(Follow(follower_id=current_user.id, following_id=target.id))
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/users/{username}/follow", status_code=status.HTTP_204_NO_CONTENT)
def unfollow_user(
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    target = _get_active_user(db, username)
    existing = db.scalar(
        select(Follow).where(
            Follow.follower_id == current_user.id,
            Follow.following_id == target.id,
        )
    )
    if existing is not None:
        db.delete(existing)
        db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/users/{username}/followers", response_model=list[FollowRead])
def list_followers(username: str, db: Session = Depends(get_db)) -> list[FollowRead]:
    target = _get_active_user(db, username)
    rows = db.scalars(
        select(Follow).where(Follow.following_id == target.id).order_by(Follow.created_at.desc())
    ).all()
    users = {
        user.id: user
        for user in db.scalars(
            select(User).where(User.id.in_([row.follower_id for row in rows] or [target.id]))
        ).all()
    }
    return [
        FollowRead(user=AuthorBrief.model_validate(users[row.follower_id]))
        for row in rows
        if row.follower_id in users
    ]


@router.get("/users/{username}/following", response_model=list[FollowRead])
def list_following(username: str, db: Session = Depends(get_db)) -> list[FollowRead]:
    target = _get_active_user(db, username)
    rows = db.scalars(
        select(Follow).where(Follow.follower_id == target.id).order_by(Follow.created_at.desc())
    ).all()
    users = {
        user.id: user
        for user in db.scalars(
            select(User).where(User.id.in_([row.following_id for row in rows] or [target.id]))
        ).all()
    }
    return [
        FollowRead(user=AuthorBrief.model_validate(users[row.following_id]))
        for row in rows
        if row.following_id in users
    ]


@router.get("/explore/search", response_model=ExploreResults)
def explore_search(
    q: str = Query(min_length=1, max_length=80),
    db: Session = Depends(get_db),
    viewer: User | None = Depends(get_optional_user),
) -> ExploreResults:
    term = f"%{q.strip().lower()}%"
    people = db.scalars(
        select(User)
        .where(
            User.is_active.is_(True),
            or_(
                User.username.ilike(term),
                User.display_name.ilike(term),
            ),
        )
        .order_by(User.username.asc())
        .limit(20)
    ).all()
    posts = db.scalars(
        select(Post)
        .options(selectinload(Post.author))
        .where(Post.body.ilike(term))
        .order_by(Post.created_at.desc())
        .limit(20)
    ).all()
    return ExploreResults(
        people=[AuthorBrief.model_validate(user) for user in people],
        posts=[_post_read(db, post, viewer) for post in posts],
    )
