from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import Severity, TaskStatus


class QuickNoteCreate(BaseModel):
    content: str
    entity_type: str | None = None
    entity_id: int | None = None


class QuickNoteUpdate(BaseModel):
    content: str


class QuickNoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    entity_type: str | None
    entity_id: int | None
    content: str
    created_at: datetime
    updated_at: datetime


class TaskItemCreate(BaseModel):
    title: str
    description: str | None = None
    priority: Severity = Severity.MEDIUM
    cve_id: int | None = None
    due_at: datetime | None = None


class TaskItemUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    priority: Severity | None = None
    due_at: datetime | None = None


class TaskItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    description: str | None
    status: TaskStatus
    priority: Severity
    cve_id: int | None
    due_at: datetime | None
    created_at: datetime
