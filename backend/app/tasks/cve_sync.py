from app.core.logging import get_logger
from app.db.session import AsyncSessionLocal
from app.repositories.cve_repo import CVERepository
from app.services.cve_service import CVEService

logger = get_logger(__name__)


async def run_cve_sync_job() -> None:
    async with AsyncSessionLocal() as session:
        service = CVEService(CVERepository(session))
        cves = await service.sync_from_sources(count=5)
        logger.info("CVE sync job completed: %d records processed", len(cves))
