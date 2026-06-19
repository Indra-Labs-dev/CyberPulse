from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.productivity_repo import ProductivityRepository
from app.schemas.productivity import (
    QuickNoteCreate,
    QuickNoteOut,
    QuickNoteUpdate,
    TaskItemCreate,
    TaskItemOut,
    TaskItemUpdate,
)
from app.services.productivity_service import ProductivityService

router = APIRouter(prefix="/productivity", tags=["productivity"])


def get_productivity_service(db: AsyncSession = Depends(get_db)) -> ProductivityService:
    return ProductivityService(ProductivityRepository(db))


@router.get("/notes", response_model=list[QuickNoteOut])
async def list_notes(
    current_user: User = Depends(get_current_user), service: ProductivityService = Depends(get_productivity_service)
) -> list[QuickNoteOut]:
    notes = await service.list_notes(current_user.id)
    return [QuickNoteOut.model_validate(n) for n in notes]


@router.post("/notes", response_model=QuickNoteOut, status_code=status.HTTP_201_CREATED)
async def create_note(
    data: QuickNoteCreate,
    current_user: User = Depends(get_current_user),
    service: ProductivityService = Depends(get_productivity_service),
) -> QuickNoteOut:
    note = await service.create_note(current_user.id, data)
    return QuickNoteOut.model_validate(note)


@router.patch("/notes/{note_id}", response_model=QuickNoteOut)
async def update_note(
    note_id: int,
    data: QuickNoteUpdate,
    current_user: User = Depends(get_current_user),
    service: ProductivityService = Depends(get_productivity_service),
) -> QuickNoteOut:
    note = await service.update_note(note_id, current_user.id, data.content)
    return QuickNoteOut.model_validate(note)


@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    service: ProductivityService = Depends(get_productivity_service),
) -> None:
    await service.delete_note(note_id, current_user.id)


@router.get("/tasks", response_model=list[TaskItemOut])
async def list_tasks(
    current_user: User = Depends(get_current_user), service: ProductivityService = Depends(get_productivity_service)
) -> list[TaskItemOut]:
    tasks = await service.list_tasks(current_user.id)
    return [TaskItemOut.model_validate(t) for t in tasks]


@router.post("/tasks", response_model=TaskItemOut, status_code=status.HTTP_201_CREATED)
async def create_task(
    data: TaskItemCreate,
    current_user: User = Depends(get_current_user),
    service: ProductivityService = Depends(get_productivity_service),
) -> TaskItemOut:
    task = await service.create_task(current_user.id, data)
    return TaskItemOut.model_validate(task)


@router.patch("/tasks/{task_id}", response_model=TaskItemOut)
async def update_task(
    task_id: int,
    data: TaskItemUpdate,
    current_user: User = Depends(get_current_user),
    service: ProductivityService = Depends(get_productivity_service),
) -> TaskItemOut:
    task = await service.update_task(task_id, current_user.id, data)
    return TaskItemOut.model_validate(task)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    service: ProductivityService = Depends(get_productivity_service),
) -> None:
    await service.delete_task(task_id, current_user.id)
