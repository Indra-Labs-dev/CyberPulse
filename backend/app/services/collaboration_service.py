from __future__ import annotations

import re

from app.models.collaboration import ActivityLogEntry, Comment, SavedSearch
from app.models.enums import AlertType, CommentEntityType, Severity
from app.repositories.alert_repo import AlertRepository
from app.repositories.collaboration_repo import CollaborationRepository
from app.repositories.user_repo import UserRepository
from app.schemas.alert import AlertCreate
from app.services.alert_service import AlertService

_MENTION_PATTERN = re.compile(r"@(\w+)")


class CollaborationService:
    def __init__(self, repo: CollaborationRepository, user_repo: UserRepository, alert_repo: AlertRepository) -> None:
        self.repo = repo
        self.user_repo = user_repo
        self.alert_service = AlertService(alert_repo)

    async def list_comments(self, entity_type: CommentEntityType, entity_id: int) -> list[Comment]:
        return await self.repo.list_comments(entity_type, entity_id)

    async def add_comment(
        self, user_id: int, entity_type: CommentEntityType, entity_id: int, content: str
    ) -> Comment:
        usernames = set(_MENTION_PATTERN.findall(content))
        mentioned_user_ids: list[int] = []
        for username in usernames:
            user = await self.user_repo.get_by_username(username)
            if user and user.id != user_id:
                mentioned_user_ids.append(user.id)

        comment = await self.repo.create_comment(
            Comment(
                entity_type=entity_type,
                entity_id=entity_id,
                user_id=user_id,
                content=content,
                mentioned_user_ids=mentioned_user_ids,
            )
        )

        author = await self.user_repo.get_by_id(user_id)
        author_name = author.username if author else "Quelqu'un"

        await self.repo.create_activity(
            ActivityLogEntry(
                user_id=user_id,
                action="COMMENT",
                description=f"{author_name} a commenté {entity_type.value} #{entity_id}",
            )
        )

        for mentioned_id in mentioned_user_ids:
            await self.alert_service.create(
                AlertCreate(
                    user_id=mentioned_id,
                    type=AlertType.SYSTEM,
                    severity=Severity.LOW,
                    message=f"{author_name} vous a mentionné dans un commentaire sur {entity_type.value} #{entity_id}",
                )
            )

        return comment

    async def list_saved_searches(self, user_id: int) -> list[SavedSearch]:
        return await self.repo.list_saved_searches(user_id)

    async def save_search(
        self, user_id: int, name: str, entity_type: str, filters: dict, is_shared: bool
    ) -> SavedSearch:
        search = await self.repo.create_saved_search(
            SavedSearch(user_id=user_id, name=name, entity_type=entity_type, filters=filters, is_shared=is_shared)
        )
        if is_shared:
            author = await self.user_repo.get_by_id(user_id)
            await self.repo.create_activity(
                ActivityLogEntry(
                    user_id=user_id,
                    action="SHARE_SEARCH",
                    description=f"{author.username if author else 'Quelqu un'} a partagé la recherche « {name} »",
                )
            )
        return search

    async def list_activity(self, limit: int = 50) -> list[ActivityLogEntry]:
        return await self.repo.list_activity(limit)
