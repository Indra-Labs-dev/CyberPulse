from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import PlaybookTriggerType, ScanStatus


class PlaybookAction(BaseModel):
    type: str
    config: dict = {}


class PlaybookCreate(BaseModel):
    name: str
    description: str | None = None
    trigger_type: PlaybookTriggerType = PlaybookTriggerType.MANUAL
    trigger_config: dict = {}
    actions: list[PlaybookAction]
    is_active: bool = True


class PlaybookUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    trigger_type: PlaybookTriggerType | None = None
    trigger_config: dict | None = None
    actions: list[PlaybookAction] | None = None
    is_active: bool | None = None


class PlaybookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    trigger_type: PlaybookTriggerType
    trigger_config: dict | None
    actions: list
    is_active: bool
    created_by: int
    created_at: datetime


class PlaybookRunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    playbook_id: int
    trigger_source: str
    status: ScanStatus
    log: str | None
    started_at: datetime
    finished_at: datetime | None


class PlaybookTemplate(BaseModel):
    name: str
    description: str
    trigger_type: PlaybookTriggerType
    trigger_config: dict
    actions: list[PlaybookAction]
