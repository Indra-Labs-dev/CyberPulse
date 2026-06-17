from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.enums import AlertStatus
from app.models.user import User
from app.repositories.alert_repo import AlertRepository
from app.schemas.alert import AlertOut
from app.services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["alerts"])


def get_alert_service(db: AsyncSession = Depends(get_db)) -> AlertService:
    return AlertService(AlertRepository(db))


@router.get("", response_model=list[AlertOut])
async def list_alerts(
    status: AlertStatus | None = None,
    current_user: User = Depends(get_current_user),
    service: AlertService = Depends(get_alert_service),
) -> list[AlertOut]:
    alerts = await service.list_for_user(current_user.id, status)
    return [AlertOut.model_validate(a) for a in alerts]


@router.post("/{alert_id}/acknowledge", response_model=AlertOut)
async def acknowledge_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    service: AlertService = Depends(get_alert_service),
) -> AlertOut:
    alert = await service.acknowledge(alert_id, current_user.id)
    return AlertOut.model_validate(alert)
