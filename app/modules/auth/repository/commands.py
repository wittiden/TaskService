from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.model.refresh_token import RefreshTokenModel


class RefreshTokenCommandsRepository:
    """Репозиторий для insert, update, delete команд"""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

    async def insert_refresh_token_data(self, refresh_token_id: UUID, user_id: UUID, issued_at: datetime, expired_at: datetime, audience: str, version: int) -> RefreshTokenModel:
        refresh_token_model = RefreshTokenModel(refresh_token_id=refresh_token_id, user_id=user_id, issued_at=issued_at, expired_at=expired_at, audience=audience, version=version)
        self._async_session.add(refresh_token_model)

        await self._async_session.flush()
        return refresh_token_model

    async def update_refresh_token_revoked_param(self, refresh_token_id: UUID):
        pass