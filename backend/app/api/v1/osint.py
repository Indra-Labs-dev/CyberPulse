from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.enums import OsintType, UserRole
from app.models.user import User
from app.repositories.osint_repo import OsintRepository
from app.schemas.osint import OsintLookupRequest, OsintResultOut
from app.services.osint_service import OsintService

router = APIRouter(prefix="/osint", tags=["osint"])


def get_osint_service(db: AsyncSession = Depends(get_db)) -> OsintService:
    return OsintService(OsintRepository(db))


@router.get("", response_model=list[OsintResultOut])
async def list_results(
    type: OsintType | None = None,
    current_user: User = Depends(get_current_user),
    service: OsintService = Depends(get_osint_service),
) -> list[OsintResultOut]:
    results = await service.list(current_user.id, type)
    return [OsintResultOut.model_validate(r) for r in results]


@router.post(
    "/lookup",
    response_model=OsintResultOut,
    dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.ANALYST))],
)
async def lookup(
    data: OsintLookupRequest,
    current_user: User = Depends(get_current_user),
    service: OsintService = Depends(get_osint_service),
) -> OsintResultOut:
    result = await service.lookup(data.type, data.target, current_user.id)
    return OsintResultOut.model_validate(result)
