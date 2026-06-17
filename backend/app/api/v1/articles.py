from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_roles
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.article_repo import ArticleRepository
from app.schemas.scraped_article import ArticleFilters, ScrapedArticleDetail, ScrapedArticleOut
from app.services.scraping_service import ScrapingService

router = APIRouter(prefix="/articles", tags=["articles"])


def get_article_repo(db: AsyncSession = Depends(get_db)) -> ArticleRepository:
    return ArticleRepository(db)


def get_scraping_service(db: AsyncSession = Depends(get_db)) -> ScrapingService:
    return ScrapingService(ArticleRepository(db))


@router.get("", response_model=list[ScrapedArticleOut])
async def list_articles(
    source: str | None = None,
    category: str | None = None,
    search: str | None = None,
    is_favorite: bool | None = None,
    is_read: bool | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    repo: ArticleRepository = Depends(get_article_repo),
) -> list[ScrapedArticleOut]:
    filters = ArticleFilters(source=source, category=category, search=search, is_favorite=is_favorite, is_read=is_read)
    articles, _total = await repo.list(filters, page, page_size)
    return [ScrapedArticleOut.model_validate(a) for a in articles]


@router.get("/{article_id}", response_model=ScrapedArticleDetail)
async def get_article(article_id: int, repo: ArticleRepository = Depends(get_article_repo)) -> ScrapedArticleDetail:
    article = await repo.get_by_id(article_id)
    if not article:
        raise NotFoundError("Article not found")
    return ScrapedArticleDetail.model_validate(article)


@router.post("/{article_id}/favorite", response_model=ScrapedArticleOut)
async def toggle_favorite(
    article_id: int,
    current_user: User = Depends(get_current_user),
    repo: ArticleRepository = Depends(get_article_repo),
) -> ScrapedArticleOut:
    article = await repo.get_by_id(article_id)
    if not article:
        raise NotFoundError("Article not found")
    article.is_favorite = not article.is_favorite
    article = await repo.update(article)
    return ScrapedArticleOut.model_validate(article)


@router.post("/{article_id}/read", response_model=ScrapedArticleOut)
async def mark_read(
    article_id: int,
    current_user: User = Depends(get_current_user),
    repo: ArticleRepository = Depends(get_article_repo),
) -> ScrapedArticleOut:
    article = await repo.get_by_id(article_id)
    if not article:
        raise NotFoundError("Article not found")
    article.is_read = True
    article = await repo.update(article)
    return ScrapedArticleOut.model_validate(article)


@router.post(
    "/scrape",
    response_model=list[ScrapedArticleOut],
    dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.ANALYST))],
)
async def trigger_scrape(service: ScrapingService = Depends(get_scraping_service)) -> list[ScrapedArticleOut]:
    articles = await service.run_pipeline()
    return [ScrapedArticleOut.model_validate(a) for a in articles]
