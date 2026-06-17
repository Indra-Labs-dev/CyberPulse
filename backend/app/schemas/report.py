from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import ReportFormat, ReportType
from app.schemas.cve import CVEFilters


class ReportCreate(BaseModel):
    title: str
    type: ReportType
    format: ReportFormat = ReportFormat.PDF
    filters: CVEFilters | None = None


class ReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    type: ReportType
    format: ReportFormat
    file_path: str | None
    created_by: int
    created_at: datetime
