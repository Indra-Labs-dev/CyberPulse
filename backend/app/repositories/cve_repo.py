from datetime import datetime

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cve import CVE
from app.models.enums import Severity
from app.schemas.cve import CVEFilters


class CVERepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, cve_pk: int) -> CVE | None:
        return await self.session.get(CVE, cve_pk)

    async def get_by_cve_id(self, cve_id: str) -> CVE | None:
        result = await self.session.execute(select(CVE).where(CVE.cve_id == cve_id))
        return result.scalar_one_or_none()

    async def list(self, filters: CVEFilters, page: int = 1, page_size: int = 20) -> tuple[list[CVE], int]:
        query = select(CVE)

        if filters.cvss_min is not None:
            query = query.where(CVE.cvss_score >= filters.cvss_min)
        if filters.cvss_max is not None:
            query = query.where(CVE.cvss_score <= filters.cvss_max)
        if filters.severity is not None:
            query = query.where(CVE.severity == filters.severity)
        if filters.date_from is not None:
            query = query.where(CVE.published_at >= filters.date_from)
        if filters.date_to is not None:
            query = query.where(CVE.published_at <= filters.date_to)
        if filters.product:
            query = query.where(func.json_contains(CVE.affected_products, f'"{filters.product}"'))
        if filters.search:
            like = f"%{filters.search}%"
            query = query.where(or_(CVE.title.ilike(like), CVE.description.ilike(like), CVE.cve_id.ilike(like)))

        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(count_query)).scalar_one()

        query = query.order_by(CVE.published_at.desc()).offset((page - 1) * page_size).limit(page_size)
        result = await self.session.execute(query)
        return list(result.scalars().all()), total

    async def create(self, cve: CVE) -> CVE:
        self.session.add(cve)
        await self.session.commit()
        await self.session.refresh(cve)
        return cve

    async def update(self, cve: CVE) -> CVE:
        cve.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(cve)
        return cve

    async def upsert_from_sync(self, cve_data: dict) -> tuple[CVE, bool]:
        existing = await self.get_by_cve_id(cve_data["cve_id"])
        if existing:
            for key, value in cve_data.items():
                setattr(existing, key, value)
            existing.updated_at = datetime.utcnow()
            await self.session.commit()
            await self.session.refresh(existing)
            return existing, False

        cve = CVE(**cve_data)
        self.session.add(cve)
        await self.session.commit()
        await self.session.refresh(cve)
        return cve, True
