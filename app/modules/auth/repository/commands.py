from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.infrastructure.database.models.refresh_token import RefreshTokenModel


class RefreshTokenCommandsRepository:
    """Репозиторий для create, update, delete команд для аутентификации"""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

    async def insert_refresh_token_data(self, refresh_token: RefreshTokenModel) -> RefreshTokenModel:
        self._async_session.add(refresh_token)

        try:
            await self._async_session.flush()
            return refresh_token
        except IntegrityError:
            await self._async_session.rollback()
            raise

    async def alter_refresh_token_data(self, refresh_token: RefreshTokenModel, new_data: dict[str, Any]) -> RefreshTokenModel:
        for key, value in new_data.items():
            setattr(refresh_token, key, value)

        try:
            await self._async_session.flush()
            return refresh_token
        except IntegrityError:
            await self._async_session.rollback()
            raise

    async def delete_refresh_token(self, refresh_token: RefreshTokenModel) -> None:
        await self._async_session.delete(refresh_token)
        await self._async_session.flush()
