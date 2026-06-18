from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AttackTechniqueOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    technique_id: str
    name: str
    tactic: str
    description: str | None


class CveAttackMappingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cve_id: int
    technique_id: int
    confidence: float
    created_at: datetime


class AttackMatrixEntry(BaseModel):
    technique: AttackTechniqueOut
    mapped_cve_count: int


class AttackMatrix(BaseModel):
    tactics: dict[str, list[AttackMatrixEntry]]


class HeatmapEntry(BaseModel):
    technique_id: str
    name: str
    tactic: str
    count: int
