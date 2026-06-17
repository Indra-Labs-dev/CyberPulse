from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.watchlist import Watchlist
from app.repositories.watchlist_repo import WatchlistRepository
from app.schemas.watchlist import WatchlistCreate, WatchlistUpdate


class WatchlistService:
    def __init__(self, watchlist_repo: WatchlistRepository) -> None:
        self.watchlist_repo = watchlist_repo

    async def list_for_user(self, user_id: int) -> list[Watchlist]:
        return await self.watchlist_repo.list_for_user(user_id)

    async def get_owned(self, watchlist_id: int, user_id: int) -> Watchlist:
        watchlist = await self.watchlist_repo.get_by_id(watchlist_id)
        if not watchlist:
            raise NotFoundError("Watchlist entry not found")
        if watchlist.user_id != user_id:
            raise ForbiddenError("You do not own this watchlist entry")
        return watchlist

    async def create(self, user_id: int, data: WatchlistCreate) -> Watchlist:
        watchlist = Watchlist(user_id=user_id, **data.model_dump())
        return await self.watchlist_repo.create(watchlist)

    async def update(self, watchlist_id: int, user_id: int, data: WatchlistUpdate) -> Watchlist:
        watchlist = await self.get_owned(watchlist_id, user_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(watchlist, key, value)
        return await self.watchlist_repo.update(watchlist)

    async def delete(self, watchlist_id: int, user_id: int) -> None:
        watchlist = await self.get_owned(watchlist_id, user_id)
        await self.watchlist_repo.delete(watchlist)
