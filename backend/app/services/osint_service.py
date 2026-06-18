from __future__ import annotations

import hashlib

import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.models.enums import OsintType
from app.models.osint import OsintResult
from app.repositories.osint_repo import OsintRepository

logger = get_logger(__name__)


def _placeholder(message: str, **extra: object) -> dict:
    return {"status": "placeholder", "message": message, **extra}


class OsintService:
    def __init__(self, repo: OsintRepository) -> None:
        self.repo = repo

    async def lookup(self, type_: OsintType, target: str, user_id: int | None) -> OsintResult:
        handler = {
            OsintType.EMAIL_BREACH: self._lookup_hibp,
            OsintType.IP_LOOKUP: self._lookup_shodan,
            OsintType.DOMAIN_LOOKUP: self._lookup_shodan,
            OsintType.GITHUB_DORK: self._lookup_github,
            OsintType.PASTEBIN: self._lookup_pastebin,
            OsintType.CERT_TRANSPARENCY: self._lookup_crtsh,
        }[type_]

        result_payload, source = await handler(target)

        osint_result = OsintResult(type=type_, target=target, result=result_payload, source=source, user_id=user_id)
        return await self.repo.create(osint_result)

    async def list(self, user_id: int | None, type_: OsintType | None) -> list[OsintResult]:
        return await self.repo.list(user_id, type_)

    async def _lookup_hibp(self, email: str) -> tuple[dict, str]:
        if not settings.hibp_api_key:
            return (
                _placeholder(
                    "Configurez HIBP_API_KEY pour interroger Have I Been Pwned en direct.",
                    target=email,
                ),
                "haveibeenpwned.com (non configuré)",
            )
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
                    headers={"hibp-api-key": settings.hibp_api_key, "user-agent": "CyberPulse"},
                )
                if response.status_code == 404:
                    return {"breaches": []}, "haveibeenpwned.com"
                response.raise_for_status()
                return {"breaches": response.json()}, "haveibeenpwned.com"
        except Exception as exc:
            logger.warning("HIBP lookup failed for %s: %s", email, exc)
            return _placeholder(f"Échec de la requête HIBP: {exc}"), "haveibeenpwned.com"

    async def _lookup_shodan(self, target: str) -> tuple[dict, str]:
        if not settings.shodan_api_key:
            return (
                _placeholder(
                    "Configurez SHODAN_API_KEY pour interroger Shodan/Censys en direct.",
                    target=target,
                ),
                "shodan.io (non configuré)",
            )
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"https://api.shodan.io/shodan/host/{target}",
                    params={"key": settings.shodan_api_key},
                )
                response.raise_for_status()
                return response.json(), "shodan.io"
        except Exception as exc:
            logger.warning("Shodan lookup failed for %s: %s", target, exc)
            return _placeholder(f"Échec de la requête Shodan: {exc}"), "shodan.io"

    async def _lookup_github(self, query: str) -> tuple[dict, str]:
        headers = {"Accept": "application/vnd.github+json"}
        if settings.github_token:
            headers["Authorization"] = f"Bearer {settings.github_token}"
        try:
            async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
                response = await client.get(
                    "https://api.github.com/search/code",
                    params={"q": query, "per_page": 10},
                )
                if response.status_code == 422 or response.status_code == 403:
                    return (
                        _placeholder(
                            "GitHub a limité la requête (non authentifiée ou requête invalide); "
                            "configurez GITHUB_TOKEN pour des quotas plus élevés.",
                            query=query,
                        ),
                        "github.com",
                    )
                response.raise_for_status()
                data = response.json()
                items = [
                    {"repository": item["repository"]["full_name"], "path": item["path"], "url": item["html_url"]}
                    for item in data.get("items", [])
                ]
                return {"total_count": data.get("total_count", 0), "items": items}, "github.com"
        except Exception as exc:
            logger.warning("GitHub dork search failed for %s: %s", query, exc)
            return _placeholder(f"Échec de la recherche GitHub: {exc}"), "github.com"

    async def _lookup_pastebin(self, target: str) -> tuple[dict, str]:
        # Pastebin does not expose a public search API; this surfaces a
        # consistent placeholder until a dedicated paste-monitoring feed
        # (e.g. a commercial dark-web/paste monitoring API) is integrated.
        digest = hashlib.sha256(target.encode("utf-8")).hexdigest()[:12]
        return (
            _placeholder(
                "La surveillance Pastebin/Dark Web nécessite une intégration tierce dédiée "
                "(pas d'API de recherche publique). Cette entrée trace la demande de surveillance.",
                target=target,
                watch_id=digest,
            ),
            "pastebin (surveillance manuelle requise)",
        )

    async def _lookup_crtsh(self, domain: str) -> tuple[dict, str]:
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get("https://crt.sh/", params={"q": domain, "output": "json"})
                response.raise_for_status()
                entries = response.json()
                certificates = [
                    {
                        "id": entry.get("id"),
                        "name_value": entry.get("name_value"),
                        "issuer_name": entry.get("issuer_name"),
                        "entry_timestamp": entry.get("entry_timestamp"),
                    }
                    for entry in entries[:50]
                ]
                return {"certificate_count": len(entries), "certificates": certificates}, "crt.sh"
        except Exception as exc:
            logger.warning("Certificate transparency lookup failed for %s: %s", domain, exc)
            return _placeholder(f"Échec de la requête crt.sh: {exc}"), "crt.sh"
