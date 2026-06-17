import hashlib

from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.enums import UserRole
from app.models.user import RefreshToken, User
from app.repositories.user_repo import UserRepository
from app.schemas.auth import RegisterRequest, TokenResponse


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class AuthService:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    async def register(self, data: RegisterRequest) -> User:
        if await self.user_repo.get_by_username(data.username):
            raise ConflictError("Username already taken")
        if await self.user_repo.get_by_email(data.email):
            raise ConflictError("Email already registered")

        user = User(
            username=data.username,
            email=data.email,
            password_hash=hash_password(data.password),
            role=data.role or UserRole.READER,
        )
        return await self.user_repo.create(user)

    async def _issue_tokens(self, user: User) -> TokenResponse:
        access_token, _, _ = create_access_token(user.id, user.role.value)
        refresh_token, jti, expires_at = create_refresh_token(user.id)

        await self.user_repo.add_refresh_token(
            RefreshToken(user_id=user.id, jti=jti, token_hash=_hash_token(refresh_token), expires_at=expires_at)
        )
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    async def login(self, username: str, password: str) -> TokenResponse:
        user = await self.user_repo.get_by_username(username)
        if not user or not verify_password(password, user.password_hash):
            raise UnauthorizedError("Invalid username or password")
        if not user.is_active:
            raise UnauthorizedError("Account is disabled")

        await self.user_repo.touch_last_login(user)
        return await self._issue_tokens(user)

    async def refresh(self, refresh_token: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)
        except Exception as exc:
            raise UnauthorizedError("Invalid refresh token") from exc

        if payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid token type")

        stored = await self.user_repo.get_refresh_token_by_jti(payload["jti"])
        if not stored or stored.revoked or stored.token_hash != _hash_token(refresh_token):
            raise UnauthorizedError("Refresh token has been revoked or is invalid")

        user = await self.user_repo.get_by_id(int(payload["sub"]))
        if not user or not user.is_active:
            raise UnauthorizedError("User not found or inactive")

        await self.user_repo.revoke_refresh_token(stored)
        return await self._issue_tokens(user)

    async def logout(self, refresh_token: str) -> None:
        try:
            payload = decode_token(refresh_token)
        except Exception:
            return
        stored = await self.user_repo.get_refresh_token_by_jti(payload.get("jti", ""))
        if stored and not stored.revoked:
            await self.user_repo.revoke_refresh_token(stored)
