from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_roles
from app.db.session import get_db
from app.models.enums import UserRole
from app.repositories.cve_repo import CVERepository
from app.repositories.mitre_repo import MitreRepository
from app.schemas.mitre import AttackMatrix, CveAttackMappingOut, HeatmapEntry
from app.services.mitre_service import MitreService

router = APIRouter(prefix="/mitre", tags=["mitre"])


def get_mitre_service(db: AsyncSession = Depends(get_db)) -> MitreService:
    return MitreService(MitreRepository(db), CVERepository(db))


@router.get("/matrix", response_model=AttackMatrix)
async def get_matrix(service: MitreService = Depends(get_mitre_service)) -> AttackMatrix:
    return await service.get_matrix()


@router.get("/heatmap", response_model=list[HeatmapEntry])
async def get_heatmap(service: MitreService = Depends(get_mitre_service)) -> list[HeatmapEntry]:
    return await service.get_heatmap()


@router.post(
    "/map/{cve_id}",
    response_model=list[CveAttackMappingOut],
    dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.ANALYST))],
)
async def map_cve(cve_id: int, service: MitreService = Depends(get_mitre_service)) -> list[CveAttackMappingOut]:
    mappings = await service.auto_map_cve(cve_id)
    return [CveAttackMappingOut.model_validate(m) for m in mappings]
