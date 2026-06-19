from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_user_from_api_key
from app.db.session import get_db
from app.models.user import User
from app.repositories.article_repo import ArticleRepository
from app.repositories.cve_repo import CVERepository
from app.schemas.cve import CVEFilters, CVEOut
from app.schemas.scraped_article import ArticleFilters, ScrapedArticleOut
from app.services.cve_service import CVEService

router = APIRouter(prefix="/public", tags=["public-api"])


@router.get("/cves", response_model=list[CVEOut])
async def public_list_cves(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _user: User = Depends(get_user_from_api_key),
    db: AsyncSession = Depends(get_db),
) -> list[CVEOut]:
    service = CVEService(CVERepository(db))
    cves, _total = await service.list(CVEFilters(), page, page_size)
    return [CVEOut.model_validate(c) for c in cves]


@router.get("/articles", response_model=list[ScrapedArticleOut])
async def public_list_articles(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _user: User = Depends(get_user_from_api_key),
    db: AsyncSession = Depends(get_db),
) -> list[ScrapedArticleOut]:
    repo = ArticleRepository(db)
    articles, _total = await repo.list(ArticleFilters(), page, page_size)
    return [ScrapedArticleOut.model_validate(a) for a in articles]
