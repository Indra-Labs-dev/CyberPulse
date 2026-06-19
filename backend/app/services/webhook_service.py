from __future__ import annotations

import httpx

from app.core.logging import get_logger
from app.models.enums import WebhookPlatform
from app.models.webhook import WebhookSubscription
from app.repositories.webhook_repo import WebhookRepository

logger = get_logger(__name__)


def _format_payload(platform: WebhookPlatform, event: str, payload: dict) -> dict:
    summary = ", ".join(f"{k}={v}" for k, v in payload.items())
    if platform == WebhookPlatform.SLACK:
        return {"text": f"*CyberPulse — {event}*\n{summary}"}
    if platform == WebhookPlatform.DISCORD:
        return {"content": f"**CyberPulse — {event}**\n{summary}"}
    if platform == WebhookPlatform.TEAMS:
        return {"text": f"CyberPulse — {event}: {summary}"}
    return {"event": event, "payload": payload}


class WebhookService:
    def __init__(self, repo: WebhookRepository) -> None:
        self.repo = repo

    async def list_for_user(self, user_id: int) -> list[WebhookSubscription]:
        return await self.repo.list_for_user(user_id)

    async def create(self, user_id: int, platform: WebhookPlatform, url: str, events: list[str]) -> WebhookSubscription:
        webhook = WebhookSubscription(platform=platform, url=url, events=events, user_id=user_id)
        return await self.repo.create(webhook)

    async def delete(self, webhook_id: int) -> None:
        webhook = await self.repo.get_by_id(webhook_id)
        if webhook:
            await self.repo.delete(webhook)

    async def dispatch_event(self, event: str, payload: dict) -> None:
        subscriptions = await self.repo.list_active()
        matching = [s for s in subscriptions if "*" in s.events or event in s.events]
        if not matching:
            return

        async with httpx.AsyncClient(timeout=8.0) as client:
            for subscription in matching:
                body = _format_payload(subscription.platform, event, payload)
                try:
                    await client.post(subscription.url, json=body)
                except Exception as exc:
                    logger.warning("Webhook delivery failed for subscription #%d: %s", subscription.id, exc)
