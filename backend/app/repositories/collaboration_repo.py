from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.collaboration import ActivityLogEntry, Comment, SavedSearch
from app.models.enums import CommentEntityType


class CollaborationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_comments(self, entity_type: CommentEntityType, entity_id: int) -> list[Comment]:
        result = await self.session.execute(
            select(Comment)
            .where(Comment.entity_type == entity_type, Comment.entity_id == entity_id)
            .order_by(Comment.created_at)
        )
        return list(result.scalars().all())

    async def create_comment(self, comment: Comment) -> Comment:
        self.session.add(comment)
        await self.session.commit()
        await self.session.refresh(comment)
        return comment

    async def list_saved_searches(self, user_id: int) -> list[SavedSearch]:
        result = await self.session.execute(
            select(SavedSearch)
            .where(or_(SavedSearch.user_id == user_id, SavedSearch.is_shared.is_(True)))
            .order_by(SavedSearch.created_at.desc())
        )
        return list(result.scalars().all())

    async def create_saved_search(self, search: SavedSearch) -> SavedSearch:
        self.session.add(search)
        await self.session.commit()
        await self.session.refresh(search)
        return search

    async def create_activity(self, entry: ActivityLogEntry) -> ActivityLogEntry:
        self.session.add(entry)
        await self.session.commit()
        await self.session.refresh(entry)
        return entry

    async def list_activity(self, limit: int = 50) -> list[ActivityLogEntry]:
        result = await self.session.execute(
            select(ActivityLogEntry).order_by(ActivityLogEntry.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())
