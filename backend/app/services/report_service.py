from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.enums import ReportFormat
from app.models.report import Report
from app.repositories.cve_repo import CVERepository
from app.repositories.report_repo import ReportRepository
from app.schemas.cve import CVEFilters
from app.schemas.report import ReportCreate
from app.services.report_engine import generate_cve_report_pdf


class ReportService:
    def __init__(self, report_repo: ReportRepository, cve_repo: CVERepository) -> None:
        self.report_repo = report_repo
        self.cve_repo = cve_repo

    async def list_for_user(self, user_id: int) -> list[Report]:
        return await self.report_repo.list_for_user(user_id)

    async def get_owned(self, report_id: int, user_id: int) -> Report:
        report = await self.report_repo.get_by_id(report_id)
        if not report:
            raise NotFoundError("Report not found")
        if report.created_by != user_id:
            raise ForbiddenError("You do not own this report")
        return report

    async def generate(self, user_id: int, data: ReportCreate) -> Report:
        filters = data.filters or CVEFilters()
        cves, _total = await self.cve_repo.list(filters, page=1, page_size=500)

        file_path = None
        if data.format == ReportFormat.PDF:
            file_path = generate_cve_report_pdf(data.title, cves)

        report = Report(
            title=data.title,
            type=data.type,
            format=data.format,
            file_path=file_path,
            content_json={"cve_ids": [cve.cve_id for cve in cves], "filters": filters.model_dump(mode="json")},
            created_by=user_id,
        )
        return await self.report_repo.create(report)
