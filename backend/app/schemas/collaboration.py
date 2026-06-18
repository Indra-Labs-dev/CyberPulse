from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import CommentEntityType


class CommentCreate(BaseModel):
    entity_type: CommentEntityType
    entity_id: int
    content: str


class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    entity_type: CommentEntityType
    entity_id: int
    user_id: int
    content: str
    mentioned_user_ids: list | None
    created_at: datetime


class SavedSearchCreate(BaseModel):
    name: str
    entity_type: str
    filters: dict
    is_shared: bool = False


class SavedSearchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    entity_type: str
    filters: dict
    is_shared: bool
    created_at: datetime


class ActivityLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None
    action: str
    description: str
    created_at: datetime
