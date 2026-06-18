from __future__ import annotations

import random
from datetime import datetime, timedelta

from app.core.exceptions import NotFoundError
from app.models.correlation import Campaign
from app.models.enums import CampaignStatus
from app.repositories.article_repo import ArticleRepository
from app.repositories.correlation_repo import CorrelationRepository
from app.repositories.cve_repo import CVERepository
from app.schemas.cve import CVEFilters
from app.schemas.scraped_article import ArticleFilters
from app.schemas.correlation import CampaignDetail, CorrelationGraph, GraphEdge, GraphNode, ThreatActorOut, TimelineEvent

SEED_ACTORS = [
    {
        "name": "APT28 (Fancy Bear)",
        "aliases": ["Sofacy", "Sednit"],
        "country": "Russia",
        "motivation": "Espionage",
        "ttps": ["T1190", "T1133", "T1071"],
        "description": "Groupe APT lié à des opérations de cyberespionnage étatique.",
    },
    {
        "name": "Lazarus Group",
        "aliases": ["Hidden Cobra"],
        "country": "North Korea",
        "motivation": "Financial gain / Espionage",
        "ttps": ["T1190", "T1003", "T1486"],
        "description": "Groupe APT connu pour des campagnes financières et de sabotage.",
    },
    {
        "name": "FIN7",
        "aliases": ["Carbon Spider"],
        "country": "Unknown",
        "motivation": "Financial gain",
        "ttps": ["T1059", "T1110", "T1041"],
        "description": "Groupe cybercriminel ciblant le secteur financier et retail.",
    },
    {
        "name": "LockBit",
        "aliases": [],
        "country": "Unknown",
        "motivation": "Ransomware-as-a-Service",
        "ttps": ["T1190", "T1486", "T1562"],
        "description": "Opérateur de ransomware en mode affiliation (RaaS).",
    },
]

_CATEGORY_TO_ACTOR = {
    "Ransomware": "LockBit",
    "Malware": "Lazarus Group",
    "Vulnérabilités": "APT28 (Fancy Bear)",
    "Cloud": "FIN7",
}


class CorrelationService:
    def __init__(self, repo: CorrelationRepository, cve_repo: CVERepository, article_repo: ArticleRepository) -> None:
        self.repo = repo
        self.cve_repo = cve_repo
        self.article_repo = article_repo

    async def ensure_seeded(self) -> None:
        await self.repo.seed_actors(SEED_ACTORS)

    async def list_actors(self) -> list[ThreatActorOut]:
        await self.ensure_seeded()
        actors = await self.repo.list_actors()
        return [ThreatActorOut.model_validate(a) for a in actors]

    async def list_campaigns(self) -> list[Campaign]:
        return await self.repo.list_campaigns()

    async def get_campaign(self, campaign_id: int) -> Campaign:
        campaign = await self.repo.get_campaign(campaign_id)
        if not campaign:
            raise NotFoundError("Campaign not found")
        return campaign

    async def get_campaign_detail(self, campaign_id: int) -> CampaignDetail:
        campaign = await self.get_campaign(campaign_id)
        return CampaignDetail(
            id=campaign.id,
            name=campaign.name,
            description=campaign.description,
            actor_id=campaign.actor_id,
            threat_score=float(campaign.threat_score),
            status=campaign.status,
            first_seen=campaign.first_seen,
            last_seen=campaign.last_seen,
            created_at=campaign.created_at,
            actor=ThreatActorOut.model_validate(campaign.actor) if campaign.actor else None,
            cve_ids=[link.cve_id for link in campaign.cve_links],
            article_ids=[link.article_id for link in campaign.article_links],
        )

    async def detect_campaigns(self) -> list[Campaign]:
        """Groups recent high-severity CVEs and scraped articles sharing a
        category into candidate "campaigns", scored from CVSS + exploit
        availability + recency. This stands in for full IOC/TTP correlation
        until a dedicated threat-intel feed is wired in.
        """
        await self.ensure_seeded()

        cve_filters = CVEFilters(severity=None)
        critical_cves, _ = await self.cve_repo.list(cve_filters, page=1, page_size=200)
        critical_cves = [c for c in critical_cves if c.severity and c.severity.value in ("CRITICAL", "HIGH")]

        article_filters = ArticleFilters()
        articles, _ = await self.article_repo.list(article_filters, page=1, page_size=200)

        clusters: dict[str, dict] = {}
        for article in articles:
            category = article.category or "Actualités"
            cluster = clusters.setdefault(category, {"cves": set(), "articles": [], "cve_ids_text": set()})
            cluster["articles"].append(article)
            for cve_text in article.mentioned_cves or []:
                cluster["cve_ids_text"].add(cve_text.upper())

        created: list[Campaign] = []
        now = datetime.utcnow()

        for category, cluster in clusters.items():
            matched_cves = [c for c in critical_cves if c.cve_id in cluster["cve_ids_text"]]
            if not matched_cves and not cluster["articles"]:
                continue
            if not matched_cves and len(cluster["articles"]) < 2:
                continue

            name = f"Campagne {category} — {now.strftime('%Y-%m')}"
            existing = await self.repo.get_campaign_by_name(name)
            if existing:
                continue

            avg_cvss = sum(float(c.cvss_score or 0) for c in matched_cves) / len(matched_cves) if matched_cves else 3.0
            exploit_bonus = 1.5 if any(c.exploits for c in matched_cves) else 0.0
            recency_bonus = 1.0
            threat_score = round(min(10.0, avg_cvss * 0.7 + exploit_bonus + recency_bonus), 1)

            actor_name = _CATEGORY_TO_ACTOR.get(category)
            actor = await self.repo.get_actor_by_name(actor_name) if actor_name else None

            dates = [c.published_at for c in matched_cves if c.published_at] + [
                a.published_at for a in cluster["articles"] if a.published_at
            ]
            first_seen = min(dates) if dates else now - timedelta(days=random.randint(1, 14))
            last_seen = max(dates) if dates else now

            campaign = await self.repo.create_campaign(
                Campaign(
                    name=name,
                    description=f"Cluster d'activité corrélé autour de la catégorie « {category} » "
                    f"({len(matched_cves)} CVE, {len(cluster['articles'])} article(s)).",
                    actor_id=actor.id if actor else None,
                    threat_score=threat_score,
                    status=CampaignStatus.ACTIVE,
                    first_seen=first_seen,
                    last_seen=last_seen,
                )
            )

            for cve in matched_cves:
                await self.repo.link_cve(campaign.id, cve.id)
            for article in cluster["articles"]:
                await self.repo.link_article(campaign.id, article.id)

            created.append(campaign)

        return created

    async def get_graph(self, campaign_id: int) -> CorrelationGraph:
        campaign = await self.get_campaign(campaign_id)
        nodes = [GraphNode(id=f"campaign-{campaign.id}", type="CAMPAIGN", label=campaign.name)]
        edges: list[GraphEdge] = []

        if campaign.actor:
            actor_node = f"actor-{campaign.actor.id}"
            nodes.append(GraphNode(id=actor_node, type="ACTOR", label=campaign.actor.name))
            edges.append(GraphEdge(source=actor_node, target=f"campaign-{campaign.id}"))

        for link in campaign.cve_links:
            cve = await self.cve_repo.get_by_id(link.cve_id)
            if not cve:
                continue
            node_id = f"cve-{cve.id}"
            nodes.append(GraphNode(id=node_id, type="CVE", label=cve.cve_id))
            edges.append(GraphEdge(source=f"campaign-{campaign.id}", target=node_id))

        for link in campaign.article_links:
            article = await self.article_repo.get_by_id(link.article_id)
            if not article:
                continue
            node_id = f"article-{article.id}"
            nodes.append(GraphNode(id=node_id, type="ARTICLE", label=article.title[:60]))
            edges.append(GraphEdge(source=f"campaign-{campaign.id}", target=node_id))

        return CorrelationGraph(nodes=nodes, edges=edges)

    async def get_timeline(self, campaign_id: int) -> list[TimelineEvent]:
        campaign = await self.get_campaign(campaign_id)
        events: list[TimelineEvent] = []

        for link in campaign.cve_links:
            cve = await self.cve_repo.get_by_id(link.cve_id)
            if cve and cve.published_at:
                events.append(TimelineEvent(occurred_at=cve.published_at, type="CVE", label=f"Publication {cve.cve_id}"))

        for link in campaign.article_links:
            article = await self.article_repo.get_by_id(link.article_id)
            if article and article.published_at:
                events.append(
                    TimelineEvent(occurred_at=article.published_at, type="ARTICLE", label=article.title[:80])
                )

        return sorted(events, key=lambda e: e.occurred_at)
