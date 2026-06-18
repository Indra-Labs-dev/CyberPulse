from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scanner import VulnScan


class ScannerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, scan_id: int) -> VulnScan | None:
        return await self.session.get(VulnScan, scan_id)

    async def list(self, user_id: int | None = None) -> list[VulnScan]:
        query = select(VulnScan)
        if user_id is not None:
            query = query.where(VulnScan.created_by == user_id)
        query = query.order_by(VulnScan.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, scan: VulnScan) -> VulnScan:
        self.session.add(scan)
        await self.session.commit()
        await self.session.refresh(scan)
        return scan

    async def update(self, scan: VulnScan) -> VulnScan:
        await self.session.commit()
        await self.session.refresh(scan)
        return scan
