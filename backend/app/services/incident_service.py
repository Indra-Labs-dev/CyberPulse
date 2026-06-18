from __future__ import annotations

from app.core.exceptions import NotFoundError
from app.models.enums import IncidentStatus
from app.models.incident import Incident, IncidentActivity
from app.repositories.incident_repo import IncidentRepository
from app.schemas.incident import IncidentCreate, IncidentMetrics, IncidentUpdate


class IncidentService:
    def __init__(self, incident_repo: IncidentRepository) -> None:
        self.incident_repo = incident_repo

    async def get(self, incident_id: int) -> Incident:
        incident = await self.incident_repo.get_by_id(incident_id)
        if not incident:
            raise NotFoundError("Incident not found")
        return incident

    async def list(self, status: IncidentStatus | None, assigned_to: int | None) -> list[Incident]:
        return await self.incident_repo.list(status, assigned_to)

    async def create(self, user_id: int, data: IncidentCreate) -> Incident:
        incident = Incident(created_by=user_id, **data.model_dump())
        incident = await self.incident_repo.create(incident)
        await self.incident_repo.add_activity(
            IncidentActivity(
                incident_id=incident.id,
                user_id=user_id,
                action="CREATED",
                message=f"Incident créé avec la sévérité {incident.severity.value}",
            )
        )
        return incident

    async def update(self, incident_id: int, user_id: int, data: IncidentUpdate) -> Incident:
        incident = await self.get(incident_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(incident, key, value)
        incident = await self.incident_repo.update(incident)
        await self.incident_repo.add_activity(
            IncidentActivity(incident_id=incident.id, user_id=user_id, action="UPDATED", message="Incident mis à jour")
        )
        return incident

    async def assign(self, incident_id: int, user_id: int, assignee_id: int) -> Incident:
        incident = await self.get(incident_id)
        incident.assigned_to = assignee_id
        incident = await self.incident_repo.update(incident)
        await self.incident_repo.add_activity(
            IncidentActivity(
                incident_id=incident.id,
                user_id=user_id,
                action="ASSIGNED",
                message=f"Assigné à l'utilisateur #{assignee_id}",
            )
        )
        return incident

    async def set_status(
        self, incident_id: int, user_id: int, status: IncidentStatus, resolution_notes: str | None
    ) -> Incident:
        incident = await self.get(incident_id)
        incident = await self.incident_repo.set_status(incident, status, resolution_notes)
        await self.incident_repo.add_activity(
            IncidentActivity(
                incident_id=incident.id,
                user_id=user_id,
                action="STATUS_CHANGE",
                message=f"Statut changé en {status.value}",
            )
        )
        return incident

    async def list_activities(self, incident_id: int) -> list[IncidentActivity]:
        return await self.incident_repo.list_activities(incident_id)

    async def metrics(self) -> IncidentMetrics:
        incidents = await self.incident_repo.list_all_for_metrics()
        total = len(incidents)
        closed = [i for i in incidents if i.status == IncidentStatus.CLOSED]
        open_count = total - len(closed)

        by_severity: dict[str, int] = {}
        for incident in incidents:
            by_severity[incident.severity.value] = by_severity.get(incident.severity.value, 0) + 1

        detection_durations = [
            (i.resolved_at - i.created_at).total_seconds() / 3600
            for i in closed
            if i.resolved_at is not None
        ]
        mttr = sum(detection_durations) / len(detection_durations) if detection_durations else None

        return IncidentMetrics(
            total=total,
            open=open_count,
            closed=len(closed),
            by_severity=by_severity,
            mttd_hours=None,
            mttr_hours=mttr,
        )
