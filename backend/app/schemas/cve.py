from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import Severity


class CVECreate(BaseModel):
    cve_id: str = Field(pattern=r"^CVE-\d{4}-\d{4,}$")
    title: str
    description: str | None = None
    cvss_score: float | None = Field(default=None, ge=0, le=10)
    cvss_vector: str | None = None
    severity: Severity | None = None
    cwe_id: str | None = None
    source: str = "NVD"
    published_at: datetime | None = None
    modified_at: datetime | None = None
    references: list[str] | None = None
    affected_products: list[str] | None = None
    exploits: list[dict] | None = None


class CVEUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    cvss_score: float | None = Field(default=None, ge=0, le=10)
    cvss_vector: str | None = None
    severity: Severity | None = None
    cwe_id: str | None = None
    references: list[str] | None = None
    affected_products: list[str] | None = None
    exploits: list[dict] | None = None


class CVEOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cve_id: str
    title: str
    description: str | None
    cvss_score: float | None
    cvss_vector: str | None
    severity: Severity | None
    cwe_id: str | None
    source: str
    published_at: datetime | None
    modified_at: datetime | None
    references: list | None
    affected_products: list | None
    exploits: list | None
    created_at: datetime
    updated_at: datetime


class CVEFilters(BaseModel):
    cvss_min: float | None = None
    cvss_max: float | None = None
    severity: Severity | None = None
    product: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    search: str | None = None
