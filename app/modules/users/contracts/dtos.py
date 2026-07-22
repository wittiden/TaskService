from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.common.enums.user import UserRoleEnum


class FullUserInfoDTO(BaseModel):
    """Схема для передачи полной информации пользователя"""

    user_id: UUID
    name: str
    email: str
    role: UserRoleEnum
    created_at: datetime
    closed_at: datetime | None
    updated_at: datetime | None
    blocked_at: datetime | None

    model_config = ConfigDict(
        from_attributes=True,
    )


class SecurityUserInfoDTO(BaseModel):
    """Схема для передачи открытой информации пользователя"""

    user_id: UUID
    name: str
    email: str
    role: UserRoleEnum

    model_config = ConfigDict(
        from_attributes=True,
    )
