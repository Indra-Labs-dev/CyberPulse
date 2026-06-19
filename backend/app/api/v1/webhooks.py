from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.webhook_repo import WebhookRepository
from app.schemas.webhook import WebhookCreate, WebhookOut
from app.services.webhook_service import WebhookService

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


def get_webhook_service(db: AsyncSession = Depends(get_db)) -> WebhookService:
    return WebhookService(WebhookRepository(db))


@router.get("", response_model=list[WebhookOut])
async def list_webhooks(
    current_user: User = Depends(get_current_user), service: WebhookService = Depends(get_webhook_service)
) -> list[WebhookOut]:
    webhooks = await service.list_for_user(current_user.id)
    return [WebhookOut.model_validate(w) for w in webhooks]


@router.post("", response_model=WebhookOut, status_code=status.HTTP_201_CREATED)
async def create_webhook(
    data: WebhookCreate,
    current_user: User = Depends(get_current_user),
    service: WebhookService = Depends(get_webhook_service),
) -> WebhookOut:
    webhook = await service.create(current_user.id, data.platform, data.url, data.events)
    return WebhookOut.model_validate(webhook)


@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(webhook_id: int, service: WebhookService = Depends(get_webhook_service)) -> None:
    await service.delete(webhook_id)
