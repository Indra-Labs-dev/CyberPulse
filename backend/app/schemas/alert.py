from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import AlertStatus, AlertType, Severity


class AlertCreate(BaseModel):
    cve_id: int | None = None
    user_id: int
    type: AlertType
    severity: Severity = Severity.MEDIUM
    message: str


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cve_id: int | None
    user_id: int
    type: AlertType
    status: AlertStatus
    severity: Severity
    message: str
    created_at: datetime
    acknowledged_at: datetime | None
