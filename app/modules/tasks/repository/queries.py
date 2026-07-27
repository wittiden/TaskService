from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.model import TaskModel


class TaskQueriesRepository:
    """Репозиторий по получению данных о задаче"""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

    async def select_user_task_by_id(self, task_id: UUID, user_id: UUID) -> TaskModel | None:
        task = await self._async_session.execute(
            select(TaskModel).where(TaskModel.task_id == task_id, TaskModel.user_id == user_id)
        )
        return task.scalar_one_or_none()

    async def select_tasks_by_user_id(
        self, user_id: UUID, offset: int = 0, limit: int = 100
    ) -> list[TaskModel]:
        tasks = await self._async_session.execute(
            select(TaskModel).where(TaskModel.user_id == user_id).offset(offset).limit(limit)
        )
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

    async def select_user_tasks_count(self, user_id: UUID) -> int:
        count = await self._async_session.execute(
            select(func.count(TaskModel.user_id)).where(TaskModel.user_id == user_id)
        )
        count = count.scalar()
        return count if count is not None else 0

    async def select_user_task_close_complete_params(
        self, user_id: UUID, task_id: UUID
    ) -> dict | None:
        columns = await self._async_session.execute(
            select(TaskModel.task_id, TaskModel.completed_at, TaskModel.closed_at).where(
                TaskModel.task_id == task_id, TaskModel.user_id == user_id
            )
        )

        columns = columns.mappings().one_or_none()
        return dict(columns) if columns else None
