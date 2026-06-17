from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.watchlist_repo import WatchlistRepository
from app.schemas.watchlist import WatchlistCreate, WatchlistOut, WatchlistUpdate
from app.services.watchlist_service import WatchlistService

router = APIRouter(prefix="/watchlists", tags=["watchlists"])


def get_watchlist_service(db: AsyncSession = Depends(get_db)) -> WatchlistService:
    return WatchlistService(WatchlistRepository(db))


@router.get("", response_model=list[WatchlistOut])
async def list_watchlists(
    current_user: User = Depends(get_current_user),
    service: WatchlistService = Depends(get_watchlist_service),
) -> list[WatchlistOut]:
    watchlists = await service.list_for_user(current_user.id)
    return [WatchlistOut.model_validate(w) for w in watchlists]


@router.post("", response_model=WatchlistOut, status_code=status.HTTP_201_CREATED)
async def create_watchlist(
    data: WatchlistCreate,
    current_user: User = Depends(get_current_user),
    service: WatchlistService = Depends(get_watchlist_service),
) -> WatchlistOut:
    watchlist = await service.create(current_user.id, data)
    return WatchlistOut.model_validate(watchlist)


@router.patch("/{watchlist_id}", response_model=WatchlistOut)
async def update_watchlist(
    watchlist_id: int,
    data: WatchlistUpdate,
    current_user: User = Depends(get_current_user),
    service: WatchlistService = Depends(get_watchlist_service),
) -> WatchlistOut:
    watchlist = await service.update(watchlist_id, current_user.id, data)
    return WatchlistOut.model_validate(watchlist)


@router.delete("/{watchlist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_watchlist(
    watchlist_id: int,
    current_user: User = Depends(get_current_user),
    service: WatchlistService = Depends(get_watchlist_service),
) -> None:
    await service.delete(watchlist_id, current_user.id)
