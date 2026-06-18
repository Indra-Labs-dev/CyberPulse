from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import IncidentStatus, Severity


class IncidentCreate(BaseModel):
    title: str
    description: str | None = None
    severity: Severity = Severity.MEDIUM
    cve_id: int | None = None
    assigned_to: int | None = None


class IncidentUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    severity: Severity | None = None
    assigned_to: int | None = None


class IncidentStatusUpdate(BaseModel):
    status: IncidentStatus
    resolution_notes: str | None = None


class IncidentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    severity: Severity
    status: IncidentStatus
    assigned_to: int | None
    cve_id: int | None
    created_by: int
    created_at: datetime
    resolved_at: datetime | None
    resolution_notes: str | None


class IncidentActivityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    incident_id: int
    user_id: int | None
    action: str
    message: str
    created_at: datetime


class IncidentMetrics(BaseModel):
    total: int
    open: int
    closed: int
    by_severity: dict[str, int]
    mttd_hours: float | None
    mttr_hours: float | None
