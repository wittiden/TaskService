from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.model import TaskModel


class TaskQueriesRepository:
    """Репозиторий по получению данных о задаче"""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

    async def select_task_by_id(self, task_id: UUID) -> TaskModel | None:
        task = await self._async_session.get(TaskModel, task_id)
        return task

    async def select_tasks_by_user_id(
        self, user_id: UUID, offset: int = 0, limit: int = 100
    ) -> list[TaskModel]:
        tasks = await self._async_session.execute(
            select(TaskModel).where(TaskModel.user_id == user_id).offset(offset).limit(limit)
        )
        return list(tasks.scalars().all())

    async def select_tasks(self, offset: int = 0, limit: int = 100) -> list[TaskModel]:
        tasks = await self._async_session.execute(select(TaskModel).offset(offset).limit(limit))
        return list(tasks.scalars().all())

    async def select_user_completed_tasks(
        self, user_id: UUID, offset: int = 0, limit: int = 100
    ) -> list[TaskModel]:
        tasks = await self._async_session.execute(
            select(TaskModel)
            .where(TaskModel.user_id == user_id, TaskModel.completed_at.is_not(None))
            .offset(offset)
            .limit(limit)
        )
        return list(tasks.scalars().all())

    async def select_user_closed_tasks(self, user_id: UUID, offset: int = 0, limit: int = 100):
        tasks = await self._async_session.execute(
            select(TaskModel)
            .where(TaskModel.user_id == user_id, TaskModel.closed_at.is_not(None))
            .offset(offset)
            .limit(limit)
        )
        return list(tasks.scalars().all())

    async def select_user_active_tasks(self, user_id: UUID, offset: int = 0, limit: int = 100):
        tasks = await self._async_session.execute(
            select(TaskModel)
            .where(
                TaskModel.user_id == user_id,
                TaskModel.completed_at.is_(None),
                TaskModel.closed_at.is_(None),
                TaskModel.completed_at.is_(None),
            )
            .offset(offset)
            .limit(limit)
        )
        return list(tasks.scalars().all())
