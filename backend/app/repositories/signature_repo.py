from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import SignatureType
from app.models.signature import Signature


class SignatureRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, signature_id: int) -> Signature | None:
        return await self.session.get(Signature, signature_id)

    async def list(self, type_: SignatureType | None = None) -> list[Signature]:
        query = select(Signature)
        if type_ is not None:
            query = query.where(Signature.type == type_)
        query = query.order_by(Signature.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, signature: Signature) -> Signature:
        self.session.add(signature)
        await self.session.commit()
        await self.session.refresh(signature)
        return signature

    async def delete(self, signature: Signature) -> None:
        await self.session.delete(signature)
        await self.session.commit()
