"""ACTIONS schemas — progress is derived from real task statuses."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.social import AuthorBrief

TaskStatus = Literal["todo", "doing", "done"]


class ActionProjectCreate(BaseModel):
    title: str = Field(min_length=2, max_length=160)
    description: str | None = Field(default=None, max_length=4000)

    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Title required.")
        return cleaned


class ActionProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None = None
    source_post_id: UUID | None = None
    created_at: datetime
    created_by: AuthorBrief
    task_total: int = 0
    task_done: int = 0
    progress_percent: int = 0


class ActionTaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    status: TaskStatus = "todo"

    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Title required.")
        return cleaned


class ActionTaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    status: TaskStatus | None = None
    position: int | None = None


class ActionTaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    title: str
    status: TaskStatus
    position: int
    assignee: AuthorBrief | None = None
    created_at: datetime


class ActionMemberAdd(BaseModel):
    username: str = Field(min_length=2, max_length=40)


class ActionMemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: str
    user: AuthorBrief


class ActionProgressRead(BaseModel):
    project_id: UUID
    task_total: int
    task_done: int
    task_doing: int
    task_todo: int
    progress_percent: int
