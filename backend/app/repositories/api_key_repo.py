from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.api_key import ApiKey


class ApiKeyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, key_id: int) -> ApiKey | None:
        return await self.session.get(ApiKey, key_id)

    async def get_by_hash(self, key_hash: str) -> ApiKey | None:
        result = await self.session.execute(select(ApiKey).where(ApiKey.key_hash == key_hash))
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: int) -> list[ApiKey]:
        result = await self.session.execute(select(ApiKey).where(ApiKey.user_id == user_id))
        return list(result.scalars().all())

    async def create(self, api_key: ApiKey) -> ApiKey:
        self.session.add(api_key)
        await self.session.commit()
        await self.session.refresh(api_key)
        return api_key

    async def update(self, api_key: ApiKey) -> ApiKey:
        await self.session.commit()
        await self.session.refresh(api_key)
        return api_key
