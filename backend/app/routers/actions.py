"""DOXAMI ACTIONS API — real task-derived progress."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.deps import get_current_user
from app.models.actions import ActionMember, ActionProject, ActionTask
from app.models.social import Post
from app.models.user import User
from app.schemas.actions import (
    ActionMemberAdd,
    ActionMemberRead,
    ActionProgressRead,
    ActionProjectCreate,
    ActionProjectRead,
    ActionTaskCreate,
    ActionTaskRead,
    ActionTaskUpdate,
)
from app.schemas.social import AuthorBrief

router = APIRouter(prefix="/actions", tags=["actions"])


def _progress(tasks: list[ActionTask]) -> tuple[int, int, int]:
    total = len(tasks)
    done = sum(1 for task in tasks if task.status == "done")
    percent = int(round((done / total) * 100)) if total else 0
    return total, done, percent


def _project_read(project: ActionProject) -> ActionProjectRead:
    total, done, percent = _progress(list(project.tasks or []))
    return ActionProjectRead(
        id=project.id,
        title=project.title,
        description=project.description,
        source_post_id=project.source_post_id,
        created_at=project.created_at,
        created_by=AuthorBrief.model_validate(project.created_by),
        task_total=total,
        task_done=done,
        progress_percent=percent,
    )


def _task_read(task: ActionTask) -> ActionTaskRead:
    return ActionTaskRead(
        id=task.id,
        project_id=task.project_id,
        title=task.title,
        status=task.status,  # type: ignore[arg-type]
        position=task.position,
        assignee=AuthorBrief.model_validate(task.assignee) if task.assignee else None,
        created_at=task.created_at,
    )


def _load_project(db: Session, project_id: UUID) -> ActionProject | None:
    return db.scalar(
        select(ActionProject)
        .options(
            selectinload(ActionProject.created_by),
            selectinload(ActionProject.tasks).selectinload(ActionTask.assignee),
            selectinload(ActionProject.members).selectinload(ActionMember.user),
        )
        .where(ActionProject.id == project_id)
    )


def _require_member(project: ActionProject, user: User) -> ActionMember | None:
    if project.created_by_id == user.id:
        return None
    for member in project.members or []:
        if member.user_id == user.id:
            return member
    raise HTTPException(status_code=403, detail="Not a project member.")


@router.get("", response_model=list[ActionProjectRead])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ActionProjectRead]:
    member_ids = select(ActionMember.project_id).where(ActionMember.user_id == current_user.id)
    projects = db.scalars(
        select(ActionProject)
        .options(
            selectinload(ActionProject.created_by),
            selectinload(ActionProject.tasks),
        )
        .where(
            or_(
                ActionProject.created_by_id == current_user.id,
                ActionProject.id.in_(member_ids),
            )
        )
        .order_by(ActionProject.created_at.desc())
        .limit(100)
    ).all()
    return [_project_read(project) for project in projects]


@router.post("", response_model=ActionProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ActionProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ActionProjectRead:
    project = ActionProject(
        title=payload.title,
        description=payload.description,
        created_by_id=current_user.id,
    )
    db.add(project)
    db.flush()
    db.add(
        ActionMember(project_id=project.id, user_id=current_user.id, role="owner")
    )
    db.commit()
    loaded = _load_project(db, project.id)
    assert loaded is not None
    return _project_read(loaded)


@router.post(
    "/from-post/{post_id}",
    response_model=ActionProjectRead,
    status_code=status.HTTP_201_CREATED,
)
def create_from_post(
    post_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ActionProjectRead:
    post = db.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found.")
    title = (post.body[:80] + "…") if len(post.body) > 80 else post.body
    project = ActionProject(
        title=title or "Action depuis un post",
        description=post.body,
        created_by_id=current_user.id,
        source_post_id=post.id,
    )
    db.add(project)
    db.flush()
    db.add(ActionMember(project_id=project.id, user_id=current_user.id, role="owner"))
    db.add(
        ActionTask(
            project_id=project.id,
            title="Définir la première étape",
            status="todo",
            position=0,
        )
    )
    db.commit()
    loaded = _load_project(db, project.id)
    assert loaded is not None
    return _project_read(loaded)


@router.get("/{project_id}", response_model=ActionProjectRead)
def get_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ActionProjectRead:
    project = _load_project(db, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")
    _require_member(project, current_user)
    return _project_read(project)


@router.get("/{project_id}/tasks", response_model=list[ActionTaskRead])
def list_tasks(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ActionTaskRead]:
    project = _load_project(db, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")
    _require_member(project, current_user)
    tasks = sorted(project.tasks or [], key=lambda item: (item.position, item.created_at))
    return [_task_read(task) for task in tasks]


@router.post(
    "/{project_id}/tasks",
    response_model=ActionTaskRead,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    project_id: UUID,
    payload: ActionTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ActionTaskRead:
    project = _load_project(db, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")
    _require_member(project, current_user)
    max_pos = db.scalar(
        select(func.coalesce(func.max(ActionTask.position), -1)).where(
            ActionTask.project_id == project_id
        )
    )
    task = ActionTask(
        project_id=project_id,
        title=payload.title,
        status=payload.status,
        position=int(max_pos) + 1,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    task = db.scalar(
        select(ActionTask)
        .options(selectinload(ActionTask.assignee))
        .where(ActionTask.id == task.id)
    )
    assert task is not None
    return _task_read(task)


@router.patch("/{project_id}/tasks/{task_id}", response_model=ActionTaskRead)
def update_task(
    project_id: UUID,
    task_id: UUID,
    payload: ActionTaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ActionTaskRead:
    project = _load_project(db, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")
    _require_member(project, current_user)
    task = next((item for item in (project.tasks or []) if item.id == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found.")
    if payload.title is not None:
        task.title = payload.title.strip()
    if payload.status is not None:
        task.status = payload.status
    if payload.position is not None:
        task.position = payload.position
    db.commit()
    db.refresh(task)
    return _task_read(task)


@router.get("/{project_id}/team", response_model=list[ActionMemberRead])
def list_team(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ActionMemberRead]:
    project = _load_project(db, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")
    _require_member(project, current_user)
    return [
        ActionMemberRead(
            id=member.id,
            role=member.role,
            user=AuthorBrief.model_validate(member.user),
        )
        for member in (project.members or [])
    ]


@router.post(
    "/{project_id}/team",
    response_model=ActionMemberRead,
    status_code=status.HTTP_201_CREATED,
)
def add_member(
    project_id: UUID,
    payload: ActionMemberAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ActionMemberRead:
    project = _load_project(db, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")
    _require_member(project, current_user)
    user = db.scalar(select(User).where(User.username == payload.username.strip().lower()))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    existing = next(
        (member for member in (project.members or []) if member.user_id == user.id),
        None,
    )
    if existing:
        return ActionMemberRead(
            id=existing.id,
            role=existing.role,
            user=AuthorBrief.model_validate(existing.user),
        )
    member = ActionMember(project_id=project_id, user_id=user.id, role="member")
    db.add(member)
    db.commit()
    db.refresh(member)
    member = db.scalar(
        select(ActionMember)
        .options(selectinload(ActionMember.user))
        .where(ActionMember.id == member.id)
    )
    assert member is not None
    return ActionMemberRead(
        id=member.id,
        role=member.role,
        user=AuthorBrief.model_validate(member.user),
    )


@router.get("/{project_id}/progress", response_model=ActionProgressRead)
def get_progress(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ActionProgressRead:
    project = _load_project(db, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")
    _require_member(project, current_user)
    tasks = list(project.tasks or [])
    total, done, percent = _progress(tasks)
    return ActionProgressRead(
        project_id=project.id,
        task_total=total,
        task_done=done,
        task_doing=sum(1 for task in tasks if task.status == "doing"),
        task_todo=sum(1 for task in tasks if task.status == "todo"),
        progress_percent=percent,
    )
