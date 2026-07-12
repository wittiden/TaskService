from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class FullUserAuditInfoDTO(BaseModel):
    """DTO для передачи полных данных аудита пользователя"""

    user_audit_id: UUID
    user_id: UUID
    field_name: str
    old_value: str | None
    new_value: str | None
    changed_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
