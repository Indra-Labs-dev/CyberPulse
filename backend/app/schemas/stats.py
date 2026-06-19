from datetime import date, datetime

from pydantic import BaseModel


class PersonalStats(BaseModel):
    reports_created: int
    incidents_created: int
    alerts_acknowledged: int
    watchlist_entries: int
    comments_posted: int


class TeamStats(BaseModel):
    total_cves: int
    total_incidents: int
    open_incidents: int
    total_reports: int
    total_alerts: int
    total_articles: int
    avg_incident_resolution_hours: float | None


class TrendPoint(BaseModel):
    date: date
    count: int


class ActivityExportEntry(BaseModel):
    user_id: int | None
    action: str
    description: str
    created_at: datetime
