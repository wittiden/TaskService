from datetime import datetime
from typing import Any
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

    name: str
    email: str
    role: UserRoleEnum

    model_config = ConfigDict(
        from_attributes=True,
    )


class FullUserAuditInfoDTO(BaseModel):
    """Схема для передачи полной информации аудита пользователя"""

    user_audits_id: UUID
    user_id: UUID
    filed_name: str
    new_value: Any
    old_value: Any | None
    changed_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
