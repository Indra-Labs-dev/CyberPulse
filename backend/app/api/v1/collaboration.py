from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.enums import CommentEntityType
from app.models.user import User
from app.repositories.alert_repo import AlertRepository
from app.repositories.collaboration_repo import CollaborationRepository
from app.repositories.user_repo import UserRepository
from app.schemas.collaboration import (
    ActivityLogOut,
    CommentCreate,
    CommentOut,
    SavedSearchCreate,
    SavedSearchOut,
)
from app.services.collaboration_service import CollaborationService

router = APIRouter(prefix="/collaboration", tags=["collaboration"])


def get_collaboration_service(db: AsyncSession = Depends(get_db)) -> CollaborationService:
    return CollaborationService(CollaborationRepository(db), UserRepository(db), AlertRepository(db))


@router.get("/comments", response_model=list[CommentOut])
async def list_comments(
    entity_type: CommentEntityType,
    entity_id: int,
    service: CollaborationService = Depends(get_collaboration_service),
) -> list[CommentOut]:
    comments = await service.list_comments(entity_type, entity_id)
    return [CommentOut.model_validate(c) for c in comments]


@router.post("/comments", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
async def create_comment(
    data: CommentCreate,
    current_user: User = Depends(get_current_user),
    service: CollaborationService = Depends(get_collaboration_service),
) -> CommentOut:
    comment = await service.add_comment(current_user.id, data.entity_type, data.entity_id, data.content)
    return CommentOut.model_validate(comment)


@router.get("/searches", response_model=list[SavedSearchOut])
async def list_searches(
    current_user: User = Depends(get_current_user),
    service: CollaborationService = Depends(get_collaboration_service),
) -> list[SavedSearchOut]:
    searches = await service.list_saved_searches(current_user.id)
    return [SavedSearchOut.model_validate(s) for s in searches]


@router.post("/searches", response_model=SavedSearchOut, status_code=status.HTTP_201_CREATED)
async def create_search(
    data: SavedSearchCreate,
    current_user: User = Depends(get_current_user),
    service: CollaborationService = Depends(get_collaboration_service),
) -> SavedSearchOut:
    search = await service.save_search(current_user.id, data.name, data.entity_type, data.filters, data.is_shared)
    return SavedSearchOut.model_validate(search)


@router.get("/activity", response_model=list[ActivityLogOut])
async def list_activity(
    limit: int = 50, service: CollaborationService = Depends(get_collaboration_service)
) -> list[ActivityLogOut]:
    activity = await service.list_activity(limit)
    return [ActivityLogOut.model_validate(a) for a in activity]
