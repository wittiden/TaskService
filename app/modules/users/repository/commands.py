from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models import UserModel


class UserCommandsRepository:
    """Репозиторий для create, update, delete команд пользователей"""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

    async def insert_user_data(self, user: UserModel) -> UserModel:
        self._async_session.add(user)

        await self._async_session.flush()
        return user

    async def alter_user_info(self, user: UserModel, new_data: dict[str, Any]) -> UserModel:
        for key, value in new_data.items():
            setattr(user, key, value)

        await self._async_session.flush()
        return user

    async def delete_user(self, user: UserModel) -> None:
        await self._async_session.delete(user)

        await self._async_session.flush()
