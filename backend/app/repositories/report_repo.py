from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.report import Report


class ReportRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, report_id: int) -> Report | None:
        return await self.session.get(Report, report_id)

    async def list_for_user(self, user_id: int) -> list[Report]:
        result = await self.session.execute(
            select(Report).where(Report.created_by == user_id).order_by(Report.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, report: Report) -> Report:
        self.session.add(report)
        await self.session.commit()
        await self.session.refresh(report)
        return report
