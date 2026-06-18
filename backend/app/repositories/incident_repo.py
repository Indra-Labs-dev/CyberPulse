from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import IncidentStatus
from app.models.incident import Incident, IncidentActivity


class IncidentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, incident_id: int) -> Incident | None:
        return await self.session.get(Incident, incident_id)

    async def list(self, status: IncidentStatus | None = None, assigned_to: int | None = None) -> list[Incident]:
        query = select(Incident)
        if status is not None:
            query = query.where(Incident.status == status)
        if assigned_to is not None:
            query = query.where(Incident.assigned_to == assigned_to)
        query = query.order_by(Incident.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_all_for_metrics(self) -> list[Incident]:
        result = await self.session.execute(select(Incident))
        return list(result.scalars().all())

    async def create(self, incident: Incident) -> Incident:
        self.session.add(incident)
        await self.session.commit()
        await self.session.refresh(incident)
        return incident

    async def update(self, incident: Incident) -> Incident:
        await self.session.commit()
        await self.session.refresh(incident)
        return incident

    async def set_status(self, incident: Incident, status: IncidentStatus, resolution_notes: str | None) -> Incident:
        incident.status = status
        if resolution_notes is not None:
            incident.resolution_notes = resolution_notes
        if status == IncidentStatus.CLOSED and incident.resolved_at is None:
            incident.resolved_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(incident)
        return incident

    async def add_activity(self, activity: IncidentActivity) -> IncidentActivity:
        self.session.add(activity)
        await self.session.commit()
        await self.session.refresh(activity)
        return activity

    async def list_activities(self, incident_id: int) -> list[IncidentActivity]:
        result = await self.session.execute(
            select(IncidentActivity)
            .where(IncidentActivity.incident_id == incident_id)
            .order_by(IncidentActivity.created_at)
        )
        return list(result.scalars().all())
