from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, RowMapping

from app.infrastructure.database.models import UserModel


class UserQueriesRepository:
    """Репозиторий для select команд пользователей"""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

    async def select_users(self, limit: int = 100, offset: int = 0) -> list[UserModel]:
        users = await self._async_session.execute(select(UserModel).limit(limit).offset(offset))
        return list(users.scalars().all())

    async def select_user_by_id(self, user_id: UUID) -> UserModel | None:
        user = await self._async_session.get(UserModel, user_id)
        return user

    async def select_user_by_email(self, email: str) -> UserModel | None:
        user = await self._async_session.execute(select(UserModel).where(UserModel.email == email))
        return user.scalar_one_or_none()

    async def select_user_id_and_closed_at(self, user_id: UUID) -> dict | None:
        obj = await self._async_session.execute(select(UserModel.user_id, UserModel.closed_at).where(UserModel.user_id == user_id))
        obj = obj.mappings().one_or_none()
        return dict(obj) if obj else None

    async def select_user_id_and_pass(self, user_id: UUID) -> dict | None:
        obj = await self._async_session.execute(select(UserModel.user_id, UserModel.password_hash, UserModel.closed_at, UserModel.blocked_at).where(UserModel.user_id == user_id))
        obj = obj.mappings().one_or_none()
        return dict(obj) if obj else None
