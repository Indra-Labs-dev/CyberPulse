from app.core.logging import get_logger
from app.db.session import AsyncSessionLocal
from app.repositories.alert_repo import AlertRepository
from app.repositories.cve_repo import CVERepository
from app.repositories.incident_repo import IncidentRepository
from app.repositories.playbook_repo import PlaybookRepository
from app.repositories.report_repo import ReportRepository
from app.services.cve_service import CVEService
from app.services.playbook_service import PlaybookService

logger = get_logger(__name__)


async def run_cve_sync_job() -> None:
    async with AsyncSessionLocal() as session:
        cve_repo = CVERepository(session)
        service = CVEService(cve_repo)
        cves = await service.sync_from_sources(count=5)
        logger.info("CVE sync job completed: %d records processed", len(cves))

        playbook_service = PlaybookService(
            PlaybookRepository(session),
            AlertRepository(session),
            IncidentRepository(session),
            ReportRepository(session),
            cve_repo,
        )
        for cve in cves:
            triggered = await playbook_service.evaluate_cve_trigger(cve)
            if triggered:
                logger.info("CVE %s triggered %d playbook run(s)", cve.cve_id, len(triggered))
