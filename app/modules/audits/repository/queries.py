from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.model import TaskAuditModel, UserAuditModel


class UserAuditQueriesRepository:
    """Репозиторий для select запросов аудита пользователей"""

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


class TaskAuditQueriesRepository:
    """Репозиторий для select запросов аудита задач"""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

    async def select_task_audits(self, offset: int = 0, limit: int = 100) -> list[TaskAuditModel]:
        task_audits = await self._async_session.execute(
            select(TaskAuditModel).offset(offset).limit(limit)
        )
        return list(task_audits.scalars().all())

    async def select_task_audit_by_id(self, task_audit_id: UUID) -> TaskAuditModel | None:
        task_audit = await self._async_session.get(TaskAuditModel, task_audit_id)
        return task_audit

    async def select_task_audits_by_task_id(
        self, task_id: UUID, offset: int = 0, limit: int = 100
    ) -> list[TaskAuditModel]:
        task_audits = await self._async_session.execute(
            select(TaskAuditModel)
            .where(TaskAuditModel.task_id == task_id)
            .offset(offset)
            .limit(limit)
        )
        return list(task_audits.scalars().all())
