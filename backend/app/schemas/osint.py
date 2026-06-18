from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import OsintType


class OsintLookupRequest(BaseModel):
    type: OsintType
    target: str


class OsintResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: OsintType
    target: str
    result: dict | list | None
    source: str
    scanned_at: datetime
    user_id: int | None
