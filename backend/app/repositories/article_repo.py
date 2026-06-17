from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scraped_article import ScrapedArticle
from app.schemas.scraped_article import ArticleFilters


class ArticleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, article_id: int) -> ScrapedArticle | None:
        return await self.session.get(ScrapedArticle, article_id)

    async def get_by_hash(self, content_hash: str) -> ScrapedArticle | None:
        result = await self.session.execute(select(ScrapedArticle).where(ScrapedArticle.hash == content_hash))
        return result.scalar_one_or_none()

    async def list(self, filters: ArticleFilters, page: int = 1, page_size: int = 20) -> tuple[list[ScrapedArticle], int]:
        query = select(ScrapedArticle)

        if filters.source:
            query = query.where(ScrapedArticle.source == filters.source)
        if filters.category:
            query = query.where(ScrapedArticle.category == filters.category)
        if filters.is_favorite is not None:
            query = query.where(ScrapedArticle.is_favorite == filters.is_favorite)
        if filters.is_read is not None:
            query = query.where(ScrapedArticle.is_read == filters.is_read)
        if filters.search:
            like = f"%{filters.search}%"
            query = query.where(or_(ScrapedArticle.title.ilike(like), ScrapedArticle.summary.ilike(like)))

        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(count_query)).scalar_one()

        query = query.order_by(ScrapedArticle.published_at.desc()).offset((page - 1) * page_size).limit(page_size)
        result = await self.session.execute(query)
        return list(result.scalars().all()), total

    async def create(self, article: ScrapedArticle) -> ScrapedArticle:
        self.session.add(article)
        await self.session.commit()
        await self.session.refresh(article)
        return article

    async def update(self, article: ScrapedArticle) -> ScrapedArticle:
        await self.session.commit()
        await self.session.refresh(article)
        return article
