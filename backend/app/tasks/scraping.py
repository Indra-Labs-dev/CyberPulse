from app.core.logging import get_logger
from app.db.session import AsyncSessionLocal
from app.repositories.article_repo import ArticleRepository
from app.services.scraping_service import ScrapingService

logger = get_logger(__name__)


async def run_scraping_job() -> None:
    async with AsyncSessionLocal() as session:
        service = ScrapingService(ArticleRepository(session))
        articles = await service.run_pipeline()
        logger.info("Scraping job completed: %d new articles stored", len(articles))
