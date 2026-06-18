from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import PlaybookTriggerType
from app.models.playbook import Playbook, PlaybookRun


class PlaybookRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, playbook_id: int) -> Playbook | None:
        return await self.session.get(Playbook, playbook_id)

    async def list(self, active_only: bool = False) -> list[Playbook]:
        query = select(Playbook)
        if active_only:
            query = query.where(Playbook.is_active.is_(True))
        result = await self.session.execute(query.order_by(Playbook.created_at.desc()))
        return list(result.scalars().all())

    async def list_by_trigger(self, trigger_type: PlaybookTriggerType) -> list[Playbook]:
        result = await self.session.execute(
            select(Playbook).where(Playbook.trigger_type == trigger_type, Playbook.is_active.is_(True))
        )
        return list(result.scalars().all())

    async def create(self, playbook: Playbook) -> Playbook:
        self.session.add(playbook)
        await self.session.commit()
        await self.session.refresh(playbook)
        return playbook

    async def update(self, playbook: Playbook) -> Playbook:
        await self.session.commit()
        await self.session.refresh(playbook)
        return playbook

    async def delete(self, playbook: Playbook) -> None:
        await self.session.delete(playbook)
        await self.session.commit()

    async def create_run(self, run: PlaybookRun) -> PlaybookRun:
        self.session.add(run)
        await self.session.commit()
        await self.session.refresh(run)
        return run

    async def update_run(self, run: PlaybookRun) -> PlaybookRun:
        await self.session.commit()
        await self.session.refresh(run)
        return run

    async def list_runs(self, playbook_id: int) -> list[PlaybookRun]:
        result = await self.session.execute(
            select(PlaybookRun)
            .where(PlaybookRun.playbook_id == playbook_id)
            .order_by(PlaybookRun.started_at.desc())
        )
        return list(result.scalars().all())
