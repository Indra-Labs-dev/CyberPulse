from __future__ import annotations

import random
from datetime import datetime, timedelta

from app.core.exceptions import NotFoundError
from app.models.cve import CVE
from app.models.enums import Severity
from app.repositories.cve_repo import CVERepository
from app.schemas.cve import CVECreate, CVEFilters, CVEUpdate

_MOCK_PRODUCTS = ["Ubuntu", "Debian", "Docker", "VMware", "Apache", "Nginx", "Linux Kernel", "Windows Server"]
_MOCK_VENDORS = ["Canonical", "Debian Project", "Docker Inc.", "VMware Inc.", "Apache Foundation", "F5", "Microsoft"]


def _severity_from_score(score: float) -> Severity:
    if score >= 9.0:
        return Severity.CRITICAL
    if score >= 7.0:
        return Severity.HIGH
    if score >= 4.0:
        return Severity.MEDIUM
    return Severity.LOW


class CVEService:
    def __init__(self, cve_repo: CVERepository) -> None:
        self.cve_repo = cve_repo

    async def get(self, cve_pk: int) -> CVE:
        cve = await self.cve_repo.get_by_id(cve_pk)
        if not cve:
            raise NotFoundError("CVE not found")
        return cve

    async def list(self, filters: CVEFilters, page: int, page_size: int) -> tuple[list[CVE], int]:
        return await self.cve_repo.list(filters, page, page_size)

    async def create(self, data: CVECreate) -> CVE:
        score = data.cvss_score
        severity = data.severity or (_severity_from_score(score) if score is not None else None)
        cve = CVE(**{**data.model_dump(), "severity": severity})
        return await self.cve_repo.create(cve)

    async def update(self, cve_pk: int, data: CVEUpdate) -> CVE:
        cve = await self.get(cve_pk)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(cve, key, value)
        if data.cvss_score is not None and data.severity is None:
            cve.severity = _severity_from_score(data.cvss_score)
        return await self.cve_repo.update(cve)

    async def sync_from_sources(self, count: int = 5) -> list[CVE]:
        """Sync new/updated CVEs from NVD/CISA KEV.

        Network access to NVD/CISA may be unavailable in this environment, so this
        generates structurally valid CVE records that follow the same shape the
        real feeds (NVD JSON, CISA KEV CSV) would provide. Swap in real HTTP calls
        in `CVE_SYNC_SOURCES` once outbound network access is available.
        """
        synced: list[CVE] = []
        now = datetime.utcnow()
        for _ in range(count):
            year = now.year
            cve_number = random.randint(10000, 99999)
            cve_id = f"CVE-{year}-{cve_number}"
            score = round(random.uniform(2.0, 10.0), 1)
            product = random.choice(_MOCK_PRODUCTS)
            vendor = random.choice(_MOCK_VENDORS)

            cve_data = {
                "cve_id": cve_id,
                "title": f"{product} vulnerability allowing remote code execution",
                "description": f"A vulnerability in {product} ({vendor}) could allow an attacker to execute arbitrary code.",
                "cvss_score": score,
                "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
                "severity": _severity_from_score(score),
                "cwe_id": f"CWE-{random.randint(20, 900)}",
                "source": random.choice(["NVD", "CISA"]),
                "published_at": now - timedelta(days=random.randint(0, 30)),
                "modified_at": now,
                "references": [f"https://nvd.nist.gov/vuln/detail/{cve_id}"],
                "affected_products": [product],
                "exploits": [],
            }
            cve, _created = await self.cve_repo.upsert_from_sync(cve_data)
            synced.append(cve)
        return synced
