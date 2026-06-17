from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, require_roles
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.user import UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(current_user)


@router.get("/admin-check", dependencies=[Depends(require_roles(UserRole.ADMIN))])
async def admin_check() -> dict[str, bool]:
    return {"is_admin": True}
