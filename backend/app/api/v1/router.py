from fastapi import APIRouter

from app.api.v1 import (
    alerts,
    api_keys,
    articles,
    auth,
    collaboration,
    correlation,
    cves,
    health,
    import_export,
    incidents,
    mitre,
    osint,
    playbooks,
    productivity,
    public,
    reports,
    scanner,
    signatures,
    stats,
    users,
    watchlists,
    webhooks,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(cves.router)
api_router.include_router(watchlists.router)
api_router.include_router(alerts.router)
api_router.include_router(reports.router)
api_router.include_router(articles.router)
api_router.include_router(mitre.router)
api_router.include_router(incidents.router)
api_router.include_router(correlation.router)
api_router.include_router(osint.router)
api_router.include_router(playbooks.router)
api_router.include_router(scanner.router)
api_router.include_router(signatures.router)
api_router.include_router(collaboration.router)
api_router.include_router(api_keys.router)
api_router.include_router(webhooks.router)
api_router.include_router(public.router)
api_router.include_router(productivity.router)
api_router.include_router(stats.router)
api_router.include_router(import_export.router)
