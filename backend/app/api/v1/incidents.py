from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.enums import IncidentStatus
from app.models.user import User
from app.repositories.incident_repo import IncidentRepository
from app.schemas.incident import (
    IncidentActivityOut,
    IncidentCreate,
    IncidentMetrics,
    IncidentOut,
    IncidentStatusUpdate,
    IncidentUpdate,
)
from app.services.incident_service import IncidentService

router = APIRouter(prefix="/incidents", tags=["incidents"])


def get_incident_service(db: AsyncSession = Depends(get_db)) -> IncidentService:
    return IncidentService(IncidentRepository(db))


@router.get("", response_model=list[IncidentOut])
async def list_incidents(
    status: IncidentStatus | None = None,
    assigned_to: int | None = None,
    service: IncidentService = Depends(get_incident_service),
) -> list[IncidentOut]:
    incidents = await service.list(status, assigned_to)
    return [IncidentOut.model_validate(i) for i in incidents]


@router.get("/metrics", response_model=IncidentMetrics)
async def get_metrics(service: IncidentService = Depends(get_incident_service)) -> IncidentMetrics:
    return await service.metrics()


@router.get("/{incident_id}", response_model=IncidentOut)
async def get_incident(incident_id: int, service: IncidentService = Depends(get_incident_service)) -> IncidentOut:
    incident = await service.get(incident_id)
    return IncidentOut.model_validate(incident)


@router.post("", response_model=IncidentOut, status_code=status.HTTP_201_CREATED)
async def create_incident(
    data: IncidentCreate,
    current_user: User = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service),
) -> IncidentOut:
    incident = await service.create(current_user.id, data)
    return IncidentOut.model_validate(incident)


@router.patch("/{incident_id}", response_model=IncidentOut)
async def update_incident(
    incident_id: int,
    data: IncidentUpdate,
    current_user: User = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service),
) -> IncidentOut:
    incident = await service.update(incident_id, current_user.id, data)
    return IncidentOut.model_validate(incident)


@router.post("/{incident_id}/assign/{assignee_id}", response_model=IncidentOut)
async def assign_incident(
    incident_id: int,
    assignee_id: int,
    current_user: User = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service),
) -> IncidentOut:
    incident = await service.assign(incident_id, current_user.id, assignee_id)
    return IncidentOut.model_validate(incident)


@router.post("/{incident_id}/status", response_model=IncidentOut)
async def update_status(
    incident_id: int,
    data: IncidentStatusUpdate,
    current_user: User = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service),
) -> IncidentOut:
    incident = await service.set_status(incident_id, current_user.id, data.status, data.resolution_notes)
    return IncidentOut.model_validate(incident)


@router.get("/{incident_id}/activity", response_model=list[IncidentActivityOut])
async def list_activity(
    incident_id: int, service: IncidentService = Depends(get_incident_service)
) -> list[IncidentActivityOut]:
    activities = await service.list_activities(incident_id)
    return [IncidentActivityOut.model_validate(a) for a in activities]
