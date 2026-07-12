from uuid import UUID
from datetime import datetime, UTC

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.model import RefreshTokenModel


class SessionQueriesRepository:
    """Репозиторий для select запросов"""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

    async def select_refresh_tokens(self, offset: int = 0, limit: int = 100) -> list[RefreshTokenModel]:
        objs = await self._async_session.execute(select(RefreshTokenModel).offset(offset).limit(limit))
        return list(objs.scalars().all())

    async def select_user_active_refresh_tokens(self, user_id: UUID, offset: int = 0, limit: int = 100) -> list[RefreshTokenModel]:
        objs = await self._async_session.execute(select(RefreshTokenModel)
                                                 .where(RefreshTokenModel.user_id == user_id, RefreshTokenModel.revoked_at.is_(None), RefreshTokenModel.expired_at > datetime.now(UTC))
                                                 .offset(offset).limit(limit))

        return list(objs.scalars().all())

    async def select_refresh_token_by_id(self, refresh_token_id: UUID) -> RefreshTokenModel:
        obj = await self._async_session.get(RefreshTokenModel, refresh_token_id)
        return obj
