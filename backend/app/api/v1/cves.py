from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_roles
from app.db.session import get_db
from app.models.enums import Severity, UserRole
from app.repositories.cve_repo import CVERepository
from app.schemas.cve import CVECreate, CVEFilters, CVEOut, CVEUpdate
from app.services.cve_service import CVEService

router = APIRouter(prefix="/cves", tags=["cves"])


def get_cve_service(db: AsyncSession = Depends(get_db)) -> CVEService:
    return CVEService(CVERepository(db))


@router.get("", response_model=list[CVEOut])
async def list_cves(
    cvss_min: float | None = None,
    cvss_max: float | None = None,
    severity: Severity | None = None,
    product: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    search: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    service: CVEService = Depends(get_cve_service),
) -> list[CVEOut]:
    filters = CVEFilters(
        cvss_min=cvss_min,
        cvss_max=cvss_max,
        severity=severity,
        product=product,
        date_from=date_from,
        date_to=date_to,
        search=search,
    )
    cves, _total = await service.list(filters, page, page_size)
    return [CVEOut.model_validate(cve) for cve in cves]


@router.get("/{cve_pk}", response_model=CVEOut)
async def get_cve(cve_pk: int, service: CVEService = Depends(get_cve_service)) -> CVEOut:
    cve = await service.get(cve_pk)
    return CVEOut.model_validate(cve)


@router.post(
    "",
    response_model=CVEOut,
    status_code=201,
    dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.ANALYST))],
)
async def create_cve(data: CVECreate, service: CVEService = Depends(get_cve_service)) -> CVEOut:
    cve = await service.create(data)
    return CVEOut.model_validate(cve)


@router.patch(
    "/{cve_pk}",
    response_model=CVEOut,
    dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.ANALYST))],
)
async def update_cve(cve_pk: int, data: CVEUpdate, service: CVEService = Depends(get_cve_service)) -> CVEOut:
    cve = await service.update(cve_pk, data)
    return CVEOut.model_validate(cve)


@router.post(
    "/sync",
    response_model=list[CVEOut],
    dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.ANALYST))],
)
async def sync_cves(count: int = Query(default=5, ge=1, le=50), service: CVEService = Depends(get_cve_service)) -> list[CVEOut]:
    cves = await service.sync_from_sources(count)
    return [CVEOut.model_validate(cve) for cve in cves]
