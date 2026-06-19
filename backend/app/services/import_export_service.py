from __future__ import annotations

import csv
import io
import json
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

from app.models.cve import CVE
from app.models.enums import Severity
from app.repositories.article_repo import ArticleRepository
from app.repositories.cve_repo import CVERepository
from app.repositories.watchlist_repo import WatchlistRepository
from app.schemas.cve import CVEFilters
from app.schemas.import_export import BackupBundle, ImportResult


def _severity_from_score(score: float | None) -> Severity | None:
    if score is None:
        return None
    if score >= 9.0:
        return Severity.CRITICAL
    if score >= 7.0:
        return Severity.HIGH
    if score >= 4.0:
        return Severity.MEDIUM
    return Severity.LOW


class ImportExportService:
    def __init__(
        self, cve_repo: CVERepository, watchlist_repo: WatchlistRepository, article_repo: ArticleRepository
    ) -> None:
        self.cve_repo = cve_repo
        self.watchlist_repo = watchlist_repo
        self.article_repo = article_repo

    # ---- Import ---------------------------------------------------------

    async def import_cves_json(self, raw: bytes) -> ImportResult:
        errors: list[str] = []
        imported = updated = 0
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            return ImportResult(imported=0, updated=0, errors=[f"JSON invalide: {exc}"])

        items = payload.get("cve_items", payload) if isinstance(payload, dict) else payload
        if not isinstance(items, list):
            return ImportResult(imported=0, updated=0, errors=["Format inattendu: une liste de CVE était attendue."])

        for index, item in enumerate(items):
            try:
                cve_id = item["cve_id"]
                score = item.get("cvss_score")
                data = {
                    "cve_id": cve_id,
                    "title": item.get("title", cve_id),
                    "description": item.get("description"),
                    "cvss_score": score,
                    "cvss_vector": item.get("cvss_vector"),
                    "severity": Severity(item["severity"]) if item.get("severity") else _severity_from_score(score),
                    "cwe_id": item.get("cwe_id"),
                    "source": item.get("source", "IMPORT"),
                    "published_at": datetime.fromisoformat(item["published_at"]) if item.get("published_at") else None,
                    "modified_at": datetime.utcnow(),
                    "references": item.get("references", []),
                    "affected_products": item.get("affected_products", []),
                    "exploits": item.get("exploits", []),
                }
                _cve, created = await self.cve_repo.upsert_from_sync(data)
                if created:
                    imported += 1
                else:
                    updated += 1
            except Exception as exc:
                errors.append(f"Ligne {index + 1}: {exc}")

        return ImportResult(imported=imported, updated=updated, errors=errors)

    async def import_cves_csv(self, raw: bytes) -> ImportResult:
        errors: list[str] = []
        imported = updated = 0
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            return ImportResult(imported=0, updated=0, errors=[f"Encodage invalide: {exc}"])

        reader = csv.DictReader(io.StringIO(text))
        for index, row in enumerate(reader):
            try:
                cve_id = row["cve_id"].strip()
                score = float(row["cvss_score"]) if row.get("cvss_score") else None
                data = {
                    "cve_id": cve_id,
                    "title": row.get("title") or cve_id,
                    "description": row.get("description") or None,
                    "cvss_score": score,
                    "cvss_vector": row.get("cvss_vector") or None,
                    "severity": Severity(row["severity"]) if row.get("severity") else _severity_from_score(score),
                    "cwe_id": row.get("cwe_id") or None,
                    "source": row.get("source") or "IMPORT",
                    "published_at": None,
                    "modified_at": datetime.utcnow(),
                    "references": [],
                    "affected_products": [p.strip() for p in row.get("affected_products", "").split(";") if p.strip()],
                    "exploits": [],
                }
                _cve, created = await self.cve_repo.upsert_from_sync(data)
                if created:
                    imported += 1
                else:
                    updated += 1
            except Exception as exc:
                errors.append(f"Ligne {index + 2}: {exc}")

        return ImportResult(imported=imported, updated=updated, errors=errors)

    # ---- Export -----------------------------------------------------------

    async def _get_cves(self, filters: CVEFilters) -> list[CVE]:
        cves, _total = await self.cve_repo.list(filters, page=1, page_size=1000)
        return cves

    async def export_json(self, filters: CVEFilters) -> str:
        cves = await self._get_cves(filters)
        data = [
            {
                "cve_id": c.cve_id,
                "title": c.title,
                "description": c.description,
                "cvss_score": float(c.cvss_score) if c.cvss_score is not None else None,
                "severity": c.severity.value if c.severity else None,
                "source": c.source,
                "published_at": c.published_at.isoformat() if c.published_at else None,
                "affected_products": c.affected_products or [],
                "references": c.references or [],
            }
            for c in cves
        ]
        return json.dumps(data, indent=2, ensure_ascii=False)

    async def export_csv(self, filters: CVEFilters) -> str:
        cves = await self._get_cves(filters)
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["cve_id", "title", "cvss_score", "severity", "source", "published_at", "affected_products"])
        for c in cves:
            writer.writerow(
                [
                    c.cve_id,
                    c.title,
                    c.cvss_score,
                    c.severity.value if c.severity else "",
                    c.source,
                    c.published_at.isoformat() if c.published_at else "",
                    ";".join(c.affected_products or []),
                ]
            )
        return buffer.getvalue()

    async def export_xml(self, filters: CVEFilters) -> str:
        cves = await self._get_cves(filters)
        root = ET.Element("cves")
        for c in cves:
            node = ET.SubElement(root, "cve")
            ET.SubElement(node, "id").text = c.cve_id
            ET.SubElement(node, "title").text = c.title
            ET.SubElement(node, "cvss_score").text = str(c.cvss_score) if c.cvss_score is not None else ""
            ET.SubElement(node, "severity").text = c.severity.value if c.severity else ""
            ET.SubElement(node, "source").text = c.source
        return ET.tostring(root, encoding="unicode", xml_declaration=True)

    async def export_stix(self, filters: CVEFilters) -> str:
        cves = await self._get_cves(filters)
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        objects = []
        for c in cves:
            objects.append(
                {
                    "type": "indicator",
                    "spec_version": "2.1",
                    "id": f"indicator--{uuid.uuid4()}",
                    "created": now,
                    "modified": now,
                    "name": c.title,
                    "description": c.description or "",
                    "indicator_types": ["vulnerability"],
                    "pattern": f"[vulnerability:id = '{c.cve_id}']",
                    "pattern_type": "stix",
                    "valid_from": now,
                    "x_cvss_score": float(c.cvss_score) if c.cvss_score is not None else None,
                    "x_severity": c.severity.value if c.severity else None,
                }
            )
        bundle = {"type": "bundle", "id": f"bundle--{uuid.uuid4()}", "objects": objects}
        return json.dumps(bundle, indent=2, ensure_ascii=False)

    async def export_misp(self, filters: CVEFilters) -> str:
        cves = await self._get_cves(filters)
        attributes = [
            {
                "type": "vulnerability",
                "category": "External analysis",
                "value": c.cve_id,
                "comment": c.title,
                "to_ids": True,
            }
            for c in cves
        ]
        event = {
            "Event": {
                "info": "CyberPulse CVE Export",
                "date": datetime.utcnow().date().isoformat(),
                "threat_level_id": "2",
                "analysis": "1",
                "Attribute": attributes,
            }
        }
        return json.dumps(event, indent=2, ensure_ascii=False)

    async def export_openioc(self, filters: CVEFilters) -> str:
        cves = await self._get_cves(filters)
        root = ET.Element("ioc", attrib={"id": str(uuid.uuid4()), "last-modified": datetime.utcnow().isoformat()})
        short_description = ET.SubElement(root, "short_description")
        short_description.text = "CyberPulse CVE Export"
        definition = ET.SubElement(root, "definition")
        indicator_or = ET.SubElement(definition, "Indicator", attrib={"operator": "OR", "id": str(uuid.uuid4())})
        for c in cves:
            item = ET.SubElement(
                indicator_or, "IndicatorItem", attrib={"id": str(uuid.uuid4()), "condition": "is"}
            )
            ET.SubElement(item, "Context", attrib={"document": "Vulnerability", "search": "Vulnerability/CVE-ID"})
            content = ET.SubElement(item, "Content", attrib={"type": "string"})
            content.text = c.cve_id
        return ET.tostring(root, encoding="unicode", xml_declaration=True)

    # ---- Backup / Restore ---------------------------------------------

    async def backup(self) -> BackupBundle:
        cves = await self._get_cves(CVEFilters())
        watchlists = await self.watchlist_repo.list_all()
        from app.schemas.scraped_article import ArticleFilters

        articles, _total = await self.article_repo.list(ArticleFilters(), page=1, page_size=1000)

        return BackupBundle(
            cves=[
                {
                    "cve_id": c.cve_id,
                    "title": c.title,
                    "description": c.description,
                    "cvss_score": float(c.cvss_score) if c.cvss_score is not None else None,
                    "severity": c.severity.value if c.severity else None,
                    "source": c.source,
                    "published_at": c.published_at.isoformat() if c.published_at else None,
                    "affected_products": c.affected_products or [],
                    "references": c.references or [],
                }
                for c in cves
            ],
            watchlists=[
                {"product_name": w.product_name, "vendor": w.vendor, "alert_threshold": w.alert_threshold.value}
                for w in watchlists
            ],
            articles=[
                {
                    "source": a.source,
                    "title": a.title,
                    "summary": a.summary,
                    "category": a.category,
                    "hash": a.hash,
                }
                for a in articles
            ],
        )

    async def restore_cves(self, bundle: BackupBundle) -> ImportResult:
        return await self.import_cves_json(json.dumps(bundle.cves).encode("utf-8"))
