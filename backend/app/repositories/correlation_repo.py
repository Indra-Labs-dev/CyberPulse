from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.correlation import Campaign, CampaignArticle, CampaignCve, ThreatActor


class CorrelationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_actors(self) -> list[ThreatActor]:
        result = await self.session.execute(select(ThreatActor))
        return list(result.scalars().all())

    async def get_actor_by_name(self, name: str) -> ThreatActor | None:
        result = await self.session.execute(select(ThreatActor).where(ThreatActor.name == name))
        return result.scalar_one_or_none()

    async def seed_actors(self, actors: list[dict]) -> None:
        for data in actors:
            existing = await self.get_actor_by_name(data["name"])
            if not existing:
                self.session.add(ThreatActor(**data))
        await self.session.commit()

    async def list_campaigns(self) -> list[Campaign]:
        result = await self.session.execute(
            select(Campaign).options(selectinload(Campaign.actor)).order_by(Campaign.threat_score.desc())
        )
        return list(result.scalars().all())

    async def get_campaign(self, campaign_id: int) -> Campaign | None:
        result = await self.session.execute(
            select(Campaign)
            .where(Campaign.id == campaign_id)
            .options(
                selectinload(Campaign.actor),
                selectinload(Campaign.cve_links),
                selectinload(Campaign.article_links),
            )
        )
        return result.scalar_one_or_none()

    async def get_campaign_by_name(self, name: str) -> Campaign | None:
        result = await self.session.execute(select(Campaign).where(Campaign.name == name))
        return result.scalar_one_or_none()

    async def create_campaign(self, campaign: Campaign) -> Campaign:
        self.session.add(campaign)
        await self.session.commit()
        await self.session.refresh(campaign)
        return campaign

    async def link_cve(self, campaign_id: int, cve_id: int) -> None:
        existing = await self.session.execute(
            select(CampaignCve).where(CampaignCve.campaign_id == campaign_id, CampaignCve.cve_id == cve_id)
        )
        if existing.scalar_one_or_none():
            return
        self.session.add(CampaignCve(campaign_id=campaign_id, cve_id=cve_id))
        await self.session.commit()

    async def link_article(self, campaign_id: int, article_id: int) -> None:
        existing = await self.session.execute(
            select(CampaignArticle).where(
                CampaignArticle.campaign_id == campaign_id, CampaignArticle.article_id == article_id
            )
        )
        if existing.scalar_one_or_none():
            return
        self.session.add(CampaignArticle(campaign_id=campaign_id, article_id=article_id))
        await self.session.commit()
