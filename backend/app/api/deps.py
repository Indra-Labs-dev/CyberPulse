from collections.abc import Callable

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_token
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.user_repo import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not token:
        raise UnauthorizedError("Missing authentication token")

    try:
        payload = decode_token(token)
    except jwt.ExpiredSignatureError as exc:
        raise UnauthorizedError("Token has expired") from exc
    except jwt.PyJWTError as exc:
        raise UnauthorizedError("Invalid authentication token") from exc

    if payload.get("type") != "access":
        raise UnauthorizedError("Invalid token type")

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(int(payload["sub"]))
    if not user or not user.is_active:
        raise UnauthorizedError("User not found or inactive")
    return user


def require_roles(*roles: UserRole) -> Callable:
    async def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise ForbiddenError("You do not have permission to perform this action")
        return current_user

    return dependency
