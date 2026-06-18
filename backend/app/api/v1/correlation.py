from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_roles
from app.db.session import get_db
from app.models.enums import UserRole
from app.repositories.article_repo import ArticleRepository
from app.repositories.correlation_repo import CorrelationRepository
from app.repositories.cve_repo import CVERepository
from app.schemas.correlation import CampaignDetail, CampaignOut, CorrelationGraph, ThreatActorOut, TimelineEvent
from app.services.correlation_service import CorrelationService

router = APIRouter(prefix="/correlation", tags=["correlation"])


def get_correlation_service(db: AsyncSession = Depends(get_db)) -> CorrelationService:
    return CorrelationService(CorrelationRepository(db), CVERepository(db), ArticleRepository(db))


@router.get("/actors", response_model=list[ThreatActorOut])
async def list_actors(service: CorrelationService = Depends(get_correlation_service)) -> list[ThreatActorOut]:
    return await service.list_actors()


@router.get("/campaigns", response_model=list[CampaignOut])
async def list_campaigns(service: CorrelationService = Depends(get_correlation_service)) -> list[CampaignOut]:
    campaigns = await service.list_campaigns()
    return [CampaignOut.model_validate(c) for c in campaigns]


@router.get("/campaigns/{campaign_id}", response_model=CampaignDetail)
async def get_campaign(
    campaign_id: int, service: CorrelationService = Depends(get_correlation_service)
) -> CampaignDetail:
    return await service.get_campaign_detail(campaign_id)


@router.get("/campaigns/{campaign_id}/graph", response_model=CorrelationGraph)
async def get_graph(
    campaign_id: int, service: CorrelationService = Depends(get_correlation_service)
) -> CorrelationGraph:
    return await service.get_graph(campaign_id)


@router.get("/campaigns/{campaign_id}/timeline", response_model=list[TimelineEvent])
async def get_timeline(
    campaign_id: int, service: CorrelationService = Depends(get_correlation_service)
) -> list[TimelineEvent]:
    return await service.get_timeline(campaign_id)


@router.post(
    "/detect",
    response_model=list[CampaignOut],
    dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.ANALYST))],
)
async def detect_campaigns(service: CorrelationService = Depends(get_correlation_service)) -> list[CampaignOut]:
    campaigns = await service.detect_campaigns()
    return [CampaignOut.model_validate(c) for c in campaigns]
