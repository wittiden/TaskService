from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.common.enums.users import UserRoleEnum


class SecurityUserInfoDTO(BaseModel):
    """Схема для безопасной передачи данных пользователя"""

    name: str
    email: str
    role: UserRoleEnum

    model_config = ConfigDict(from_attributes=True)


class UserInfoDTO(BaseModel):
    """Схема для полной передачи данных пользователя"""

    user_id: UUID
    name: str
    email: str
    role: UserRoleEnum
    created_at: datetime
    closed_at: datetime | None
    updated_at: datetime | None
    blocked_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
