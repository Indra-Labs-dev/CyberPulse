from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mitre import AttackTechnique, CveAttackMapping


class MitreRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_techniques(self) -> list[AttackTechnique]:
        result = await self.session.execute(select(AttackTechnique).order_by(AttackTechnique.tactic))
        return list(result.scalars().all())

    async def get_technique_by_code(self, technique_id: str) -> AttackTechnique | None:
        result = await self.session.execute(
            select(AttackTechnique).where(AttackTechnique.technique_id == technique_id)
        )
        return result.scalar_one_or_none()

    async def seed_techniques(self, techniques: list[dict]) -> None:
        for data in techniques:
            existing = await self.get_technique_by_code(data["technique_id"])
            if not existing:
                self.session.add(AttackTechnique(**data))
        await self.session.commit()

    async def create_mapping(self, mapping: CveAttackMapping) -> CveAttackMapping:
        self.session.add(mapping)
        await self.session.commit()
        await self.session.refresh(mapping)
        return mapping

    async def mapping_exists(self, cve_id: int, technique_id: int) -> bool:
        result = await self.session.execute(
            select(CveAttackMapping).where(
                CveAttackMapping.cve_id == cve_id, CveAttackMapping.technique_id == technique_id
            )
        )
        return result.scalar_one_or_none() is not None

    async def mapping_counts(self) -> dict[int, int]:
        result = await self.session.execute(
            select(CveAttackMapping.technique_id, func.count(CveAttackMapping.id)).group_by(
                CveAttackMapping.technique_id
            )
        )
        return {row[0]: row[1] for row in result.all()}

    async def mappings_for_cve(self, cve_id: int) -> list[CveAttackMapping]:
        result = await self.session.execute(
            select(CveAttackMapping).where(CveAttackMapping.cve_id == cve_id)
        )
        return list(result.scalars().all())
