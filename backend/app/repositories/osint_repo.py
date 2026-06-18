from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import OsintType
from app.models.osint import OsintResult


class OsintRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, result_id: int) -> OsintResult | None:
        return await self.session.get(OsintResult, result_id)

    async def list(self, user_id: int | None = None, type_: OsintType | None = None) -> list[OsintResult]:
        query = select(OsintResult)
        if user_id is not None:
            query = query.where(OsintResult.user_id == user_id)
        if type_ is not None:
            query = query.where(OsintResult.type == type_)
        query = query.order_by(OsintResult.scanned_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, osint_result: OsintResult) -> OsintResult:
        self.session.add(osint_result)
        await self.session.commit()
        await self.session.refresh(osint_result)
        return osint_result
