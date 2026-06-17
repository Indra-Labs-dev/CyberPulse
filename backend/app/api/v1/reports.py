from fastapi import APIRouter, Depends, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_roles
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.cve_repo import CVERepository
from app.repositories.report_repo import ReportRepository
from app.schemas.report import ReportCreate, ReportOut
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


def get_report_service(db: AsyncSession = Depends(get_db)) -> ReportService:
    return ReportService(ReportRepository(db), CVERepository(db))


@router.get("", response_model=list[ReportOut])
async def list_reports(
    current_user: User = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
) -> list[ReportOut]:
    reports = await service.list_for_user(current_user.id)
    return [ReportOut.model_validate(r) for r in reports]


@router.post(
    "",
    response_model=ReportOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.ANALYST))],
)
async def generate_report(
    data: ReportCreate,
    current_user: User = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
) -> ReportOut:
    report = await service.generate(current_user.id, data)
    return ReportOut.model_validate(report)


@router.get("/{report_id}/download")
async def download_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
) -> FileResponse:
    report = await service.get_owned(report_id, current_user.id)
    if not report.file_path:
        raise NotFoundError("Report file not available")
    return FileResponse(report.file_path, media_type="application/pdf", filename=f"{report.title}.pdf")
