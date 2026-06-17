from fastapi import APIRouter

from app.api.v1 import alerts, articles, auth, cves, health, reports, users, watchlists

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(cves.router)
api_router.include_router(watchlists.router)
api_router.include_router(alerts.router)
api_router.include_router(reports.router)
api_router.include_router(articles.router)
