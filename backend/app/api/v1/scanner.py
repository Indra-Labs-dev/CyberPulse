from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.cve_repo import CVERepository
from app.repositories.scanner_repo import ScannerRepository
from app.schemas.scanner import PortScanRequest, VulnScanOut
from app.services.scanner_service import ScannerService
from app.tasks.scheduler import scheduler
from app.tasks.vuln_scan import run_scheduled_port_scan

router = APIRouter(prefix="/scanner", tags=["scanner"])


def get_scanner_service(db: AsyncSession = Depends(get_db)) -> ScannerService:
    return ScannerService(ScannerRepository(db), CVERepository(db))


@router.get("", response_model=list[VulnScanOut])
async def list_scans(
    current_user: User = Depends(get_current_user), service: ScannerService = Depends(get_scanner_service)
) -> list[VulnScanOut]:
    scans = await service.list(current_user.id)
    return [VulnScanOut.model_validate(s) for s in scans]


@router.get("/{scan_id}", response_model=VulnScanOut)
async def get_scan(scan_id: int, service: ScannerService = Depends(get_scanner_service)) -> VulnScanOut:
    scan = await service.get(scan_id)
    return VulnScanOut.model_validate(scan)


@router.post(
    "/port-scan",
    response_model=VulnScanOut,
    dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.ANALYST))],
)
async def port_scan(
    data: PortScanRequest,
    current_user: User = Depends(get_current_user),
    service: ScannerService = Depends(get_scanner_service),
) -> VulnScanOut:
    scan = await service.run_port_scan(data.target, data.ports, current_user.id, data.schedule_minutes)

    if data.schedule_minutes:
        scheduler.add_job(
            run_scheduled_port_scan,
            trigger="interval",
            minutes=data.schedule_minutes,
            id=f"vulnscan-{scan.id}",
            replace_existing=True,
            args=[scan.id],
        )

    return VulnScanOut.model_validate(scan)


@router.post(
    "/file-scan",
    response_model=VulnScanOut,
    dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.ANALYST))],
)
async def file_scan(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    service: ScannerService = Depends(get_scanner_service),
) -> VulnScanOut:
    raw = await file.read()
    content = raw.decode("utf-8", errors="ignore")
    scan = await service.run_file_scan(file.filename or "uploaded_file", content, current_user.id)
    return VulnScanOut.model_validate(scan)
