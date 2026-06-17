from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import Severity


class WatchlistCreate(BaseModel):
    product_name: str
    vendor: str | None = None
    version_pattern: str | None = None
    alert_threshold: Severity = Severity.MEDIUM


class WatchlistUpdate(BaseModel):
    product_name: str | None = None
    vendor: str | None = None
    version_pattern: str | None = None
    alert_threshold: Severity | None = None


class WatchlistOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    product_name: str
    vendor: str | None
    version_pattern: str | None
    alert_threshold: Severity
    created_at: datetime
