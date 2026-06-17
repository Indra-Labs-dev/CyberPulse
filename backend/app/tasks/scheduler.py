from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import settings
from app.core.logging import get_logger
from app.tasks.cve_sync import run_cve_sync_job
from app.tasks.scraping import run_scraping_job

logger = get_logger(__name__)

scheduler = AsyncIOScheduler()


def configure_scheduler() -> AsyncIOScheduler:
    if settings.cve_sync_enabled:
        scheduler.add_job(
            run_cve_sync_job,
            trigger="interval",
            minutes=settings.cve_sync_interval_minutes,
            id="cve_sync",
            replace_existing=True,
        )
        logger.info("Scheduled CVE sync job every %d minutes", settings.cve_sync_interval_minutes)

    if settings.scraping_enabled:
        scheduler.add_job(
            run_scraping_job,
            trigger="interval",
            minutes=settings.scraping_interval_minutes,
            id="scraping_pipeline",
            replace_existing=True,
        )
        logger.info("Scheduled scraping job every %d minutes", settings.scraping_interval_minutes)

    return scheduler


def start_scheduler() -> None:
    if not scheduler.running:
        configure_scheduler()
        scheduler.start()
        logger.info("Scheduler started")


def shutdown_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
