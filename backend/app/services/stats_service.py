from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert
from app.models.collaboration import ActivityLogEntry, Comment
from app.models.cve import CVE
from app.models.enums import AlertStatus, IncidentStatus
from app.models.incident import Incident
from app.models.report import Report
from app.models.scraped_article import ScrapedArticle
from app.models.watchlist import Watchlist
from app.schemas.stats import ActivityExportEntry, PersonalStats, TeamStats, TrendPoint


class StatsService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def personal_stats(self, user_id: int) -> PersonalStats:
        reports = await self.session.scalar(select(func.count()).where(Report.created_by == user_id).select_from(Report))
        incidents = await self.session.scalar(
            select(func.count()).where(Incident.created_by == user_id).select_from(Incident)
        )
        acknowledged_alerts = await self.session.scalar(
            select(func.count())
            .where(Alert.user_id == user_id, Alert.status == AlertStatus.ACKNOWLEDGED)
            .select_from(Alert)
        )
        watchlist_entries = await self.session.scalar(
            select(func.count()).where(Watchlist.user_id == user_id).select_from(Watchlist)
        )
        comments = await self.session.scalar(
            select(func.count()).where(Comment.user_id == user_id).select_from(Comment)
        )

        return PersonalStats(
            reports_created=reports or 0,
            incidents_created=incidents or 0,
            alerts_acknowledged=acknowledged_alerts or 0,
            watchlist_entries=watchlist_entries or 0,
            comments_posted=comments or 0,
        )

    async def team_stats(self) -> TeamStats:
        total_cves = await self.session.scalar(select(func.count()).select_from(CVE))
        total_incidents = await self.session.scalar(select(func.count()).select_from(Incident))
        open_incidents = await self.session.scalar(
            select(func.count()).where(Incident.status != IncidentStatus.CLOSED).select_from(Incident)
        )
        total_reports = await self.session.scalar(select(func.count()).select_from(Report))
        total_alerts = await self.session.scalar(select(func.count()).select_from(Alert))
        total_articles = await self.session.scalar(select(func.count()).select_from(ScrapedArticle))

        result = await self.session.execute(
            select(Incident.created_at, Incident.resolved_at).where(
                Incident.status == IncidentStatus.CLOSED, Incident.resolved_at.is_not(None)
            )
        )
        durations = [
            (resolved_at - created_at).total_seconds() / 3600 for created_at, resolved_at in result.all()
        ]
        avg_resolution = sum(durations) / len(durations) if durations else None

        return TeamStats(
            total_cves=total_cves or 0,
            total_incidents=total_incidents or 0,
            open_incidents=open_incidents or 0,
            total_reports=total_reports or 0,
            total_alerts=total_alerts or 0,
            total_articles=total_articles or 0,
            avg_incident_resolution_hours=avg_resolution,
        )

    async def cve_trends(self, days: int = 30) -> list[TrendPoint]:
        since = datetime.utcnow() - timedelta(days=days)
        result = await self.session.execute(
            select(func.date(CVE.published_at), func.count())
            .where(CVE.published_at.is_not(None), CVE.published_at >= since)
            .group_by(func.date(CVE.published_at))
            .order_by(func.date(CVE.published_at))
        )
        points = []
        for day_value, count in result.all():
            parsed_date = day_value if not isinstance(day_value, str) else datetime.fromisoformat(day_value).date()
            points.append(TrendPoint(date=parsed_date, count=count))
        return points

    async def activity_export(self, year: int, month: int) -> list[ActivityExportEntry]:
        start = datetime(year, month, 1)
        end = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)
        result = await self.session.execute(
            select(ActivityLogEntry)
            .where(ActivityLogEntry.created_at >= start, ActivityLogEntry.created_at < end)
            .order_by(ActivityLogEntry.created_at)
        )
        return [ActivityExportEntry.model_validate(entry, from_attributes=True) for entry in result.scalars().all()]
