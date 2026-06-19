from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.stats import ActivityExportEntry, PersonalStats, TeamStats, TrendPoint
from app.services.stats_service import StatsService

router = APIRouter(prefix="/stats", tags=["stats"])


def get_stats_service(db: AsyncSession = Depends(get_db)) -> StatsService:
    return StatsService(db)


@router.get("/personal", response_model=PersonalStats)
async def personal_stats(
    current_user: User = Depends(get_current_user), service: StatsService = Depends(get_stats_service)
) -> PersonalStats:
    return await service.personal_stats(current_user.id)


@router.get("/team", response_model=TeamStats)
async def team_stats(service: StatsService = Depends(get_stats_service)) -> TeamStats:
    return await service.team_stats()


@router.get("/trends", response_model=list[TrendPoint])
async def cve_trends(
    days: int = Query(default=30, ge=1, le=365), service: StatsService = Depends(get_stats_service)
) -> list[TrendPoint]:
    return await service.cve_trends(days)


@router.get("/activity-export", response_model=list[ActivityExportEntry])
async def activity_export(
    year: int, month: int = Query(ge=1, le=12), service: StatsService = Depends(get_stats_service)
) -> list[ActivityExportEntry]:
    return await service.activity_export(year, month)
