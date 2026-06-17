from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.watchlist import Watchlist


class WatchlistRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, watchlist_id: int) -> Watchlist | None:
        return await self.session.get(Watchlist, watchlist_id)

    async def list_for_user(self, user_id: int) -> list[Watchlist]:
        result = await self.session.execute(select(Watchlist).where(Watchlist.user_id == user_id))
        return list(result.scalars().all())

    async def list_all(self) -> list[Watchlist]:
        result = await self.session.execute(select(Watchlist))
        return list(result.scalars().all())

    async def create(self, watchlist: Watchlist) -> Watchlist:
        self.session.add(watchlist)
        await self.session.commit()
        await self.session.refresh(watchlist)
        return watchlist

    async def update(self, watchlist: Watchlist) -> Watchlist:
        await self.session.commit()
        await self.session.refresh(watchlist)
        return watchlist

    async def delete(self, watchlist: Watchlist) -> None:
        await self.session.delete(watchlist)
        await self.session.commit()
