from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.user_repo import UserRepository
from app.schemas.auth import LoginRequest, LogoutRequest, RefreshRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserOut
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(UserRepository(db))


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, service: AuthService = Depends(get_auth_service)) -> UserOut:
    user = await service.register(data)
    return UserOut.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, service: AuthService = Depends(get_auth_service)) -> TokenResponse:
    return await service.login(data.username, data.password)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest, service: AuthService = Depends(get_auth_service)) -> TokenResponse:
    return await service.refresh(data.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(data: LogoutRequest, service: AuthService = Depends(get_auth_service)) -> None:
    await service.logout(data.refresh_token)
