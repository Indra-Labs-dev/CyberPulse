from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.webhook import WebhookSubscription


class WebhookRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, webhook_id: int) -> WebhookSubscription | None:
        return await self.session.get(WebhookSubscription, webhook_id)

    async def list_for_user(self, user_id: int) -> list[WebhookSubscription]:
        result = await self.session.execute(select(WebhookSubscription).where(WebhookSubscription.user_id == user_id))
        return list(result.scalars().all())

    async def list_active(self) -> list[WebhookSubscription]:
        result = await self.session.execute(
            select(WebhookSubscription).where(WebhookSubscription.is_active.is_(True))
        )
        return list(result.scalars().all())

    async def create(self, webhook: WebhookSubscription) -> WebhookSubscription:
        self.session.add(webhook)
        await self.session.commit()
        await self.session.refresh(webhook)
        return webhook

    async def delete(self, webhook: WebhookSubscription) -> None:
        await self.session.delete(webhook)
        await self.session.commit()
