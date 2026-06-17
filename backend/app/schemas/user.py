from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.enums import UserRole


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    role: UserRole
    is_active: bool
    preferences: dict | None = None
    created_at: datetime
    last_login: datetime | None = None


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    preferences: dict | None = None


class UserRoleUpdate(BaseModel):
    role: UserRole
