from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.alert_repo import AlertRepository
from app.repositories.cve_repo import CVERepository
from app.repositories.incident_repo import IncidentRepository
from app.repositories.playbook_repo import PlaybookRepository
from app.repositories.report_repo import ReportRepository
from app.schemas.playbook import (
    PlaybookCreate,
    PlaybookOut,
    PlaybookRunOut,
    PlaybookTemplate,
    PlaybookUpdate,
)
from app.services.playbook_service import PlaybookService

router = APIRouter(prefix="/playbooks", tags=["playbooks"])


def get_playbook_service(db: AsyncSession = Depends(get_db)) -> PlaybookService:
    return PlaybookService(
        PlaybookRepository(db), AlertRepository(db), IncidentRepository(db), ReportRepository(db), CVERepository(db)
    )


@router.get("/templates", response_model=list[PlaybookTemplate])
async def list_templates(service: PlaybookService = Depends(get_playbook_service)) -> list[PlaybookTemplate]:
    return service.list_templates()


@router.get("", response_model=list[PlaybookOut])
async def list_playbooks(
    active_only: bool = False, service: PlaybookService = Depends(get_playbook_service)
) -> list[PlaybookOut]:
    playbooks = await service.list(active_only)
    return [PlaybookOut.model_validate(p) for p in playbooks]


@router.get("/{playbook_id}", response_model=PlaybookOut)
async def get_playbook(playbook_id: int, service: PlaybookService = Depends(get_playbook_service)) -> PlaybookOut:
    playbook = await service.get(playbook_id)
    return PlaybookOut.model_validate(playbook)


@router.post(
    "",
    response_model=PlaybookOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.ANALYST))],
)
async def create_playbook(
    data: PlaybookCreate,
    current_user: User = Depends(get_current_user),
    service: PlaybookService = Depends(get_playbook_service),
) -> PlaybookOut:
    playbook = await service.create(current_user.id, data)
    return PlaybookOut.model_validate(playbook)


@router.patch(
    "/{playbook_id}",
    response_model=PlaybookOut,
    dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.ANALYST))],
)
async def update_playbook(
    playbook_id: int, data: PlaybookUpdate, service: PlaybookService = Depends(get_playbook_service)
) -> PlaybookOut:
    playbook = await service.update(playbook_id, data)
    return PlaybookOut.model_validate(playbook)


@router.delete(
    "/{playbook_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.ANALYST))],
)
async def delete_playbook(playbook_id: int, service: PlaybookService = Depends(get_playbook_service)) -> None:
    await service.delete(playbook_id)


@router.post("/{playbook_id}/run", response_model=PlaybookRunOut)
async def run_playbook(
    playbook_id: int,
    current_user: User = Depends(get_current_user),
    service: PlaybookService = Depends(get_playbook_service),
) -> PlaybookRunOut:
    run = await service.run(playbook_id, current_user.id, trigger_source="MANUAL")
    return PlaybookRunOut.model_validate(run)


@router.get("/{playbook_id}/runs", response_model=list[PlaybookRunOut])
async def list_runs(
    playbook_id: int, service: PlaybookService = Depends(get_playbook_service)
) -> list[PlaybookRunOut]:
    runs = await service.list_runs(playbook_id)
    return [PlaybookRunOut.model_validate(r) for r in runs]
