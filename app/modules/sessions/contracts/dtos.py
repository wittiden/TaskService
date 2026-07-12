from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class FullRefreshTokenInfoDTO(BaseModel):
    """DTO для передачи полных данных refresh токена"""

    refresh_token_id: UUID
    user_id: UUID
    issued_at: datetime
    expired_at: datetime
    revoked_at: datetime | None
    audience: str

    model_config = ConfigDict(
        from_attributes=True,
    )
