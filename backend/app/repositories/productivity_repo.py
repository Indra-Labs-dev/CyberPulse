from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.productivity import QuickNote, TaskItem


class ProductivityRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_notes(self, user_id: int) -> list[QuickNote]:
        result = await self.session.execute(
            select(QuickNote).where(QuickNote.user_id == user_id).order_by(QuickNote.updated_at.desc())
        )
        return list(result.scalars().all())

    async def get_note(self, note_id: int) -> QuickNote | None:
        return await self.session.get(QuickNote, note_id)

    async def create_note(self, note: QuickNote) -> QuickNote:
        self.session.add(note)
        await self.session.commit()
        await self.session.refresh(note)
        return note

    async def update_note(self, note: QuickNote) -> QuickNote:
        await self.session.commit()
        await self.session.refresh(note)
        return note

    async def delete_note(self, note: QuickNote) -> None:
        await self.session.delete(note)
        await self.session.commit()

    async def list_tasks(self, user_id: int) -> list[TaskItem]:
        result = await self.session.execute(
            select(TaskItem).where(TaskItem.user_id == user_id).order_by(TaskItem.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_task(self, task_id: int) -> TaskItem | None:
        return await self.session.get(TaskItem, task_id)

    async def create_task(self, task: TaskItem) -> TaskItem:
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def update_task(self, task: TaskItem) -> TaskItem:
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def delete_task(self, task: TaskItem) -> None:
        await self.session.delete(task)
        await self.session.commit()
