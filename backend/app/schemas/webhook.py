from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import WebhookPlatform


class WebhookCreate(BaseModel):
    platform: WebhookPlatform
    url: str
    events: list[str] = ["*"]


class WebhookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    platform: WebhookPlatform
    url: str
    events: list
    is_active: bool
    user_id: int
    created_at: datetime
