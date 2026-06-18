from app.core.logging import get_logger
from app.db.session import AsyncSessionLocal
from app.repositories.cve_repo import CVERepository
from app.repositories.scanner_repo import ScannerRepository
from app.services.scanner_service import ScannerService

logger = get_logger(__name__)


async def run_scheduled_port_scan(scan_id: int) -> None:
    async with AsyncSessionLocal() as session:
        service = ScannerService(ScannerRepository(session), CVERepository(session))
        scan = await service.rerun_port_scan(scan_id)
        logger.info("Scheduled scan #%d completed: %d port(s) responded", scan_id, len(scan.findings or []))
