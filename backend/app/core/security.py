import secrets
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

import bcrypt
import jwt

from app.core.config import settings


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))


def _create_token(subject: str, token_type: TokenType, expires_delta: timedelta, extra_claims: dict[str, Any] | None = None) -> tuple[str, str, datetime]:
    now = datetime.now(timezone.utc)
    expire_at = now + expires_delta
    jti = str(uuid.uuid4())
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type.value,
        "iat": now,
        "exp": expire_at,
        "jti": jti,
    }
    if extra_claims:
        payload.update(extra_claims)
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token, jti, expire_at


def create_access_token(user_id: int, role: str) -> tuple[str, str, datetime]:
    return _create_token(
        subject=str(user_id),
        token_type=TokenType.ACCESS,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        extra_claims={"role": role},
    )


def create_refresh_token(user_id: int) -> tuple[str, str, datetime]:
    return _create_token(
        subject=str(user_id),
        token_type=TokenType.REFRESH,
        expires_delta=timedelta(days=settings.refresh_token_expire_days),
    )


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])


def generate_api_key() -> str:
    return secrets.token_urlsafe(32)
