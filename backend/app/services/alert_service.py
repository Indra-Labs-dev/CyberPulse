from app.core.exceptions import ForbiddenError, NotFoundError
from app.core.logging import get_logger
from app.models.alert import Alert
from app.models.enums import AlertStatus
from app.repositories.alert_repo import AlertRepository
from app.repositories.webhook_repo import WebhookRepository
from app.schemas.alert import AlertCreate
from app.services.webhook_service import WebhookService
from app.websocket.manager import manager

logger = get_logger(__name__)


class AlertService:
    def __init__(self, alert_repo: AlertRepository) -> None:
        self.alert_repo = alert_repo

    async def list_for_user(self, user_id: int, status: AlertStatus | None = None) -> list[Alert]:
        return await self.alert_repo.list_for_user(user_id, status)

    async def create(self, data: AlertCreate, broadcast: bool = True) -> Alert:
        alert = Alert(**data.model_dump())
        alert = await self.alert_repo.create(alert)
        if broadcast:
            await manager.broadcast_alert(
                {
                    "id": alert.id,
                    "cve_id": alert.cve_id,
                    "user_id": alert.user_id,
                    "type": alert.type.value,
                    "severity": alert.severity.value,
                    "message": alert.message,
                }
            )
            try:
                webhook_service = WebhookService(WebhookRepository(self.alert_repo.session))
                await webhook_service.dispatch_event(
                    "alert.created",
                    {"severity": alert.severity.value, "type": alert.type.value, "message": alert.message},
                )
            except Exception as exc:
                logger.warning("Webhook dispatch failed for alert #%s: %s", alert.id, exc)
        return alert

    async def acknowledge(self, alert_id: int, user_id: int) -> Alert:
        alert = await self.alert_repo.get_by_id(alert_id)
        if not alert:
            raise NotFoundError("Alert not found")
        if alert.user_id != user_id:
            raise ForbiddenError("You do not own this alert")
        return await self.alert_repo.acknowledge(alert)
