from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ApiKeyCreate(BaseModel):
    name: str
    rate_limit_per_minute: int = 60


class ApiKeyCreated(BaseModel):
    """Returned exactly once, at creation time — the raw secret is never stored or shown again."""

    id: int
    name: str
    api_key: str
    key_prefix: str


class ApiKeyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    key_prefix: str
    rate_limit_per_minute: int
    is_active: bool
    last_used_at: datetime | None
    created_at: datetime
