from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import ScanStatus, ScanType


class PortScanRequest(BaseModel):
    target: str
    ports: list[int] | None = None
    schedule_minutes: int | None = None


class VulnScanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    target: str
    scan_type: ScanType
    status: ScanStatus
    findings: list | None
    schedule_minutes: int | None
    created_by: int
    created_at: datetime
    completed_at: datetime | None
