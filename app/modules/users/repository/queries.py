from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.model import UserModel


class UserQueriesRepository:
    """Репозиторий для select запросов пользователя"""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

    async def select_user_by_id(self, user_id: UUID) -> UserModel | None:
        user = await self._async_session.get(UserModel, user_id)
        return user

    async def select_users(self, offset: int = 0, limit: int = 100) -> list[UserModel]:
        users = await self._async_session.execute(select(UserModel).offset(offset).limit(limit))
        users = users.scalars().all()
        return list(users)

    async def select_user_block_param(self, user_id: UUID) -> datetime | None:
        blocked_at = await self._async_session.execute(select(UserModel.blocked_at).where(UserModel.user_id == user_id))
        return blocked_at.scalar_one_or_none()
