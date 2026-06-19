from __future__ import annotations

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.productivity import QuickNote, TaskItem
from app.repositories.productivity_repo import ProductivityRepository
from app.schemas.productivity import QuickNoteCreate, TaskItemCreate, TaskItemUpdate


class ProductivityService:
    def __init__(self, repo: ProductivityRepository) -> None:
        self.repo = repo

    async def list_notes(self, user_id: int) -> list[QuickNote]:
        return await self.repo.list_notes(user_id)

    async def create_note(self, user_id: int, data: QuickNoteCreate) -> QuickNote:
        note = QuickNote(user_id=user_id, **data.model_dump())
        return await self.repo.create_note(note)

    async def update_note(self, note_id: int, user_id: int, content: str) -> QuickNote:
        note = await self.repo.get_note(note_id)
        if not note:
            raise NotFoundError("Note not found")
        if note.user_id != user_id:
            raise ForbiddenError("You do not own this note")
        note.content = content
        return await self.repo.update_note(note)

    async def delete_note(self, note_id: int, user_id: int) -> None:
        note = await self.repo.get_note(note_id)
        if not note:
            raise NotFoundError("Note not found")
        if note.user_id != user_id:
            raise ForbiddenError("You do not own this note")
        await self.repo.delete_note(note)

    async def list_tasks(self, user_id: int) -> list[TaskItem]:
        return await self.repo.list_tasks(user_id)

    async def create_task(self, user_id: int, data: TaskItemCreate) -> TaskItem:
        task = TaskItem(user_id=user_id, **data.model_dump())
        return await self.repo.create_task(task)

    async def update_task(self, task_id: int, user_id: int, data: TaskItemUpdate) -> TaskItem:
        task = await self.repo.get_task(task_id)
        if not task:
            raise NotFoundError("Task not found")
        if task.user_id != user_id:
            raise ForbiddenError("You do not own this task")
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(task, key, value)
        return await self.repo.update_task(task)

    async def delete_task(self, task_id: int, user_id: int) -> None:
        task = await self.repo.get_task(task_id)
        if not task:
            raise NotFoundError("Task not found")
        if task.user_id != user_id:
            raise ForbiddenError("You do not own this task")
        await self.repo.delete_task(task)
