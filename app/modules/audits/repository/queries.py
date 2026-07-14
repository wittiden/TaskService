from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.model import UserAuditModel


class UserAuditQueriesRepository:
    """Репозиторий для select запросов"""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

    async def select_user_audits(self, offset: int = 0, limit: int = 100) -> list[UserAuditModel]:
        objs = await self._async_session.execute(select(UserAuditModel).offset(offset).limit(limit))
        return list(objs.scalars().all())

    async def select_user_audits_by_user_id(
        self, user_id: UUID, offset: int = 0, limit: int = 100
    ) -> list[UserAuditModel]:
        objs = await self._async_session.execute(
            select(UserAuditModel)
            .where(UserAuditModel.user_id == user_id)
            .offset(offset)
            .limit(limit)
        )
        return list(objs.scalars().all())

    async def select_user_audit_by_id(self, user_audit_id: UUID) -> UserAuditModel | None:
        obj = await self._async_session.get(UserAuditModel, user_audit_id)
        return obj
