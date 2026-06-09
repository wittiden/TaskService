from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TokensInfoDTO(BaseModel):
    """Схема для передачи данных при входе в аккаунт"""

    access_token: str
    refresh_token: str
    token_type: str = 'Bearer'

    model_config = ConfigDict(from_attributes=True)


class FullRefreshTokenInfoDTO(BaseModel):
    """Схема для передачи полных данных refresh токена"""

    refresh_token_id: UUID
    user_id: UUID
    issued_at: datetime
    expires_at: datetime
    revoked_at: datetime | None
    version: int
    audience: str

    model_config = ConfigDict(from_attributes=True)
