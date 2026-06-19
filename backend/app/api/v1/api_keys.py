from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.api_key_repo import ApiKeyRepository
from app.repositories.user_repo import UserRepository
from app.schemas.api_key import ApiKeyCreate, ApiKeyCreated, ApiKeyOut
from app.services.api_key_service import ApiKeyService

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


def get_api_key_service(db: AsyncSession = Depends(get_db)) -> ApiKeyService:
    return ApiKeyService(ApiKeyRepository(db), UserRepository(db))


@router.get("", response_model=list[ApiKeyOut])
async def list_keys(
    current_user: User = Depends(get_current_user), service: ApiKeyService = Depends(get_api_key_service)
) -> list[ApiKeyOut]:
    keys = await service.list_keys(current_user.id)
    return [ApiKeyOut.model_validate(k) for k in keys]


@router.post("", response_model=ApiKeyCreated, status_code=status.HTTP_201_CREATED)
async def create_key(
    data: ApiKeyCreate,
    current_user: User = Depends(get_current_user),
    service: ApiKeyService = Depends(get_api_key_service),
) -> ApiKeyCreated:
    api_key, raw_key = await service.create_key(current_user.id, data.name, data.rate_limit_per_minute)
    return ApiKeyCreated(id=api_key.id, name=api_key.name, api_key=raw_key, key_prefix=api_key.key_prefix)


@router.post("/{key_id}/revoke", response_model=ApiKeyOut)
async def revoke_key(key_id: int, service: ApiKeyService = Depends(get_api_key_service)) -> ApiKeyOut:
    api_key = await service.revoke(key_id)
    return ApiKeyOut.model_validate(api_key)
