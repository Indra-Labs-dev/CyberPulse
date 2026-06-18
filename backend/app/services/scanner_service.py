from __future__ import annotations

import asyncio
import re
from datetime import datetime

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.models.enums import ScanStatus, ScanType
from app.models.scanner import VulnScan
from app.repositories.cve_repo import CVERepository
from app.repositories.scanner_repo import ScannerRepository
from app.schemas.cve import CVEFilters

logger = get_logger(__name__)

COMMON_PORTS: dict[int, str] = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    6379: "Redis",
    8080: "HTTP-alt",
    27017: "MongoDB",
}

MAX_PORTS_PER_SCAN = 50
CONNECT_TIMEOUT_SECONDS = 1.5

_SECRET_PATTERNS = [
    ("Mot de passe en clair", re.compile(r"(?i)(password|passwd|pwd)\s*[=:]\s*['\"]?[^\s'\"]{3,}")),
    ("Clé API générique", re.compile(r"(?i)(api[_-]?key|secret[_-]?key)\s*[=:]\s*['\"]?[A-Za-z0-9_\-]{8,}")),
    ("Clé AWS Access Key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("Clé privée embarquée", re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("Token JWT exposé", re.compile(r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+")),
    ("Connexion DB avec credentials en clair", re.compile(r"(?i)(mysql|postgres|mongodb)://[^:]+:[^@]+@")),
]


class ScannerService:
    """Lightweight, defensive-use vulnerability scanner.

    Intended for scanning assets the operator controls (localhost, internal
    lab hosts). The TCP connect scan is capped to a small port list and a
    short per-port timeout — this is not a mass-scanning or offensive tool.
    """

    def __init__(self, repo: ScannerRepository, cve_repo: CVERepository) -> None:
        self.repo = repo
        self.cve_repo = cve_repo

    async def get(self, scan_id: int) -> VulnScan:
        scan = await self.repo.get_by_id(scan_id)
        if not scan:
            raise NotFoundError("Scan not found")
        return scan

    async def list(self, user_id: int | None) -> list[VulnScan]:
        return await self.repo.list(user_id)

    async def _probe_port(self, target: str, port: int) -> dict | None:
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(target, port), timeout=CONNECT_TIMEOUT_SECONDS
            )
        except Exception:
            return None

        banner = ""
        try:
            data = await asyncio.wait_for(reader.read(128), timeout=0.8)
            banner = data.decode("utf-8", errors="ignore").strip()
        except Exception:
            pass
        finally:
            writer.close()

        return {
            "port": port,
            "service": COMMON_PORTS.get(port, "Inconnu"),
            "banner": banner or None,
        }

    async def _match_cves(self, service: str, banner: str | None) -> list[str]:
        filters = CVEFilters(search=service)
        cves, _total = await self.cve_repo.list(filters, page=1, page_size=10)
        matches = [c.cve_id for c in cves]
        if banner:
            version_match = re.search(r"\d+\.\d+(\.\d+)?", banner)
            if version_match:
                versioned_filters = CVEFilters(search=f"{service} {version_match.group()}")
                versioned_cves, _ = await self.cve_repo.list(versioned_filters, page=1, page_size=10)
                matches.extend(c.cve_id for c in versioned_cves if c.cve_id not in matches)
        return matches

    async def run_port_scan(self, target: str, ports: list[int] | None, user_id: int, schedule_minutes: int | None) -> VulnScan:
        ports = (ports or list(COMMON_PORTS.keys()))[:MAX_PORTS_PER_SCAN]

        scan = await self.repo.create(
            VulnScan(
                target=target,
                scan_type=ScanType.PORT_SCAN,
                status=ScanStatus.RUNNING,
                created_by=user_id,
                schedule_minutes=schedule_minutes,
            )
        )

        findings = []
        results = await asyncio.gather(*(self._probe_port(target, port) for port in ports))
        for result in results:
            if result is None:
                continue
            cve_matches = await self._match_cves(result["service"], result["banner"])
            findings.append({**result, "matched_cves": cve_matches})

        scan.findings = findings
        scan.status = ScanStatus.COMPLETED
        scan.completed_at = datetime.utcnow()
        return await self.repo.update(scan)

    async def rerun_port_scan(self, scan_id: int) -> VulnScan:
        scan = await self.get(scan_id)
        return await self.run_port_scan(scan.target, None, scan.created_by, scan.schedule_minutes)

    def scan_file_content(self, content: str) -> list[dict]:
        findings = []
        for line_number, line in enumerate(content.splitlines(), start=1):
            for label, pattern in _SECRET_PATTERNS:
                if pattern.search(line):
                    findings.append({"line": line_number, "issue": label, "excerpt": line.strip()[:200]})
        return findings

    async def run_file_scan(self, filename: str, content: str, user_id: int) -> VulnScan:
        scan = await self.repo.create(
            VulnScan(target=filename, scan_type=ScanType.FILE_SCAN, status=ScanStatus.RUNNING, created_by=user_id)
        )
        findings = self.scan_file_content(content)
        scan.findings = findings
        scan.status = ScanStatus.COMPLETED
        scan.completed_at = datetime.utcnow()
        return await self.repo.update(scan)
