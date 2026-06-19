from __future__ import annotations

import hashlib
import time
from collections import defaultdict, deque
from datetime import datetime

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import generate_api_key
from app.models.api_key import ApiKey
from app.models.user import User
from app.repositories.api_key_repo import ApiKeyRepository
from app.repositories.user_repo import UserRepository

# In-memory sliding-window rate limiter, keyed by api_key id. Acceptable for
# a single-process deployment; swap for a Redis-backed counter if/when the
# API is scaled horizontally.
_request_log: dict[int, deque] = defaultdict(deque)


def _hash_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


class ApiKeyService:
    def __init__(self, repo: ApiKeyRepository, user_repo: UserRepository) -> None:
        self.repo = repo
        self.user_repo = user_repo

    async def create_key(self, user_id: int, name: str, rate_limit_per_minute: int) -> tuple[ApiKey, str]:
        raw_key = f"cps_{generate_api_key()}"
        api_key = ApiKey(
            name=name,
            key_prefix=raw_key[:12],
            key_hash=_hash_key(raw_key),
            rate_limit_per_minute=rate_limit_per_minute,
            user_id=user_id,
        )
        created = await self.repo.create(api_key)
        return created, raw_key

    async def list_keys(self, user_id: int) -> list[ApiKey]:
        return await self.repo.list_for_user(user_id)

    async def revoke(self, key_id: int) -> ApiKey:
        api_key = await self.repo.get_by_id(key_id)
        if not api_key:
            raise UnauthorizedError("API key not found")
        api_key.is_active = False
        return await self.repo.update(api_key)

    def _check_rate_limit(self, api_key: ApiKey) -> None:
        now = time.monotonic()
        window = _request_log[api_key.id]
        while window and now - window[0] > 60:
            window.popleft()
        if len(window) >= api_key.rate_limit_per_minute:
            raise ForbiddenError(
                f"Limite de débit dépassée ({api_key.rate_limit_per_minute} requêtes/minute) pour cette clé API."
            )
        window.append(now)

    async def authenticate(self, raw_key: str) -> tuple[User, ApiKey]:
        api_key = await self.repo.get_by_hash(_hash_key(raw_key))
        if not api_key or not api_key.is_active:
            raise UnauthorizedError("Clé API invalide ou révoquée")

        self._check_rate_limit(api_key)

        user = await self.user_repo.get_by_id(api_key.user_id)
        if not user or not user.is_active:
            raise UnauthorizedError("Utilisateur associé à cette clé introuvable ou inactif")

        api_key.last_used_at = datetime.utcnow()
        await self.repo.update(api_key)

        return user, api_key
