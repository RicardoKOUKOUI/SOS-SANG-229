"""Text posts, likes, comments."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.deps import get_current_user, get_optional_user
from app.models.social import Post, PostComment, PostLike
from app.models.user import User
from app.schemas.social import (
    AuthorBrief,
    CommentCreate,
    CommentRead,
    LikeRead,
    PostCreate,
    PostRead,
)

router = APIRouter(prefix="/posts", tags=["posts"])


def _post_read(db: Session, post: Post, viewer: User | None) -> PostRead:
    like_count = db.scalar(
        select(func.count()).select_from(PostLike).where(PostLike.post_id == post.id)
    ) or 0
    comment_count = db.scalar(
        select(func.count()).select_from(PostComment).where(PostComment.post_id == post.id)
    ) or 0
    liked_by_me = False
    if viewer is not None:
        liked_by_me = (
            db.scalar(
                select(PostLike.id).where(
                    PostLike.post_id == post.id,
                    PostLike.user_id == viewer.id,
                )
            )
            is not None
        )
    return PostRead(
        id=post.id,
        body=post.body,
        created_at=post.created_at,
        author=AuthorBrief.model_validate(post.author),
        like_count=int(like_count),
        comment_count=int(comment_count),
        liked_by_me=liked_by_me,
    )


@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
def create_post(
    payload: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PostRead:
    post = Post(author_id=current_user.id, body=payload.body)
    db.add(post)
    db.commit()
    db.refresh(post)
    post = db.scalar(
        select(Post).options(selectinload(Post.author)).where(Post.id == post.id)
    )
    assert post is not None
    return _post_read(db, post, current_user)


@router.get("", response_model=list[PostRead])
def list_posts(
    tab: str = Query(default="recent", pattern="^(recent|following)$"),
    db: Session = Depends(get_db),
    viewer: User | None = Depends(get_optional_user),
) -> list[PostRead]:
    from app.models.social import Follow

    query = select(Post).options(selectinload(Post.author)).order_by(Post.created_at.desc())
    if tab == "following":
        if viewer is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required for following feed.",
            )
        following_ids = select(Follow.following_id).where(Follow.follower_id == viewer.id)
        query = query.where(Post.author_id.in_(following_ids))
    posts = db.scalars(query.limit(50)).all()
    return [_post_read(db, post, viewer) for post in posts]


@router.get("/{post_id}", response_model=PostRead)
def get_post(
    post_id: UUID,
    db: Session = Depends(get_db),
    viewer: User | None = Depends(get_optional_user),
) -> PostRead:
    post = db.scalar(
        select(Post).options(selectinload(Post.author)).where(Post.id == post_id)
    )
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    return _post_read(db, post, viewer)


@router.post("/{post_id}/likes", status_code=status.HTTP_204_NO_CONTENT)
def like_post(
    post_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    post = db.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    existing = db.scalar(
        select(PostLike).where(
            PostLike.post_id == post_id,
            PostLike.user_id == current_user.id,
        )
    )
    if existing is None:
        db.add(PostLike(post_id=post_id, user_id=current_user.id))
        db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{post_id}/likes", status_code=status.HTTP_204_NO_CONTENT)
def unlike_post(
    post_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    existing = db.scalar(
        select(PostLike).where(
            PostLike.post_id == post_id,
            PostLike.user_id == current_user.id,
        )
    )
    if existing is not None:
        db.delete(existing)
        db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{post_id}/likes", response_model=list[LikeRead])
def list_likes(post_id: UUID, db: Session = Depends(get_db)) -> list[LikeRead]:
    post = db.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    rows = db.scalars(
        select(PostLike)
        .where(PostLike.post_id == post_id)
        .order_by(PostLike.created_at.desc())
        .limit(100)
    ).all()
    if not rows:
        return []
    users = {
        user.id: user
        for user in db.scalars(select(User).where(User.id.in_([row.user_id for row in rows]))).all()
    }
    return [
        LikeRead(user=AuthorBrief.model_validate(users[row.user_id]))
        for row in rows
        if row.user_id in users
    ]


@router.get("/{post_id}/comments", response_model=list[CommentRead])
def list_comments(post_id: UUID, db: Session = Depends(get_db)) -> list[CommentRead]:
    post = db.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    comments = db.scalars(
        select(PostComment)
        .options(selectinload(PostComment.author))
        .where(PostComment.post_id == post_id)
        .order_by(PostComment.created_at.asc())
        .limit(200)
    ).all()
    return [
        CommentRead(
            id=comment.id,
            body=comment.body,
            created_at=comment.created_at,
            author=AuthorBrief.model_validate(comment.author),
        )
        for comment in comments
    ]


@router.post(
    "/{post_id}/comments",
    response_model=CommentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    post_id: UUID,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CommentRead:
    post = db.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    comment = PostComment(post_id=post_id, author_id=current_user.id, body=payload.body)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    comment = db.scalar(
        select(PostComment)
        .options(selectinload(PostComment.author))
        .where(PostComment.id == comment.id)
    )
    assert comment is not None
    return CommentRead(
        id=comment.id,
        body=comment.body,
        created_at=comment.created_at,
        author=AuthorBrief.model_validate(comment.author),
    )
