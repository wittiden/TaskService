from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.refresh_token import RefreshTokenModel


class RefreshTokenQueriesRepository:
    """Репозиторий для select запросов для аутентификации"""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

    async def select_refresh_tokens(self, limit: int = 100, offset: int = 0) -> list[RefreshTokenModel]:
        objs = await self._async_session.execute(select(RefreshTokenModel).offset(offset).limit(limit))
        return list(objs.scalars().all())

    async def select_refresh_token_by_id(self, refresh_token_id: UUID) -> RefreshTokenModel | None:
        obj = await self._async_session.get(RefreshTokenModel, refresh_token_id)
        return obj

    async def select_refresh_tokens_by_user_id(self, user_id: UUID) -> list[RefreshTokenModel]:
        objs = await self._async_session.execute(select(RefreshTokenModel).where(RefreshTokenModel.user_id == user_id))
        return list(objs.scalars().all())

    async def select_active_refresh_tokens(self, limit: int = 100, offset: int = 0) -> list[RefreshTokenModel]:
        objs = await self._async_session.execute(select(RefreshTokenModel).where(RefreshTokenModel.revoked_at is not None).offset(offset).limit(limit))
        return list(objs.scalars().all())

    async def select_revoked_refresh_tokens(self, limit: int = 100, offset: int = 0) -> list[RefreshTokenModel]:
        objs = await self._async_session.execute(select(RefreshTokenModel).where(RefreshTokenModel.revoked_at is None).offset(offset).limit(limit))
        return list(objs.scalars().all())
