from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import delete, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums.task import TaskImportantLevelEnum, TaskScheduleEnum
from app.infrastructure.database.model import TaskModel


class TaskCommandsRepository:
    """Репозиторйи по изменению данных для задач"""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

    async def insert_task(
        self,
        user_id: UUID,
        important_level: TaskImportantLevelEnum,
        schedule_type: TaskScheduleEnum,
        title: str,
        description: str | None,
    ) -> TaskModel:
        task = TaskModel(
            user_id=user_id,
            important_level=important_level,
            schedule_type=schedule_type,
            title=title,
            description=description,
        )

        try:
            self._async_session.add(task)
            await self._async_session.flush()

            return task

        except IntegrityError:
            raise

    async def delete_task_by_id(self, task_id: UUID) -> TaskModel | None:
        result = await self._async_session.execute(
            delete(TaskModel).where(TaskModel.task_id == task_id).returning(TaskModel)
        )

        return result.scalar_one_or_none()

    async def delete_user_tasks(self, user_id: UUID) -> list[TaskModel]:
        result = await self._async_session.execute(
            delete(TaskModel).where(TaskModel.user_id == user_id).returning(TaskModel)
        )

        return list(result.scalars().all())

    async def delete_close_complete_user_tasks(self, user_id: UUID) -> list[TaskModel]:
        result = await self._async_session.execute(
            delete(TaskModel)
            .where(
                TaskModel.user_id == user_id,
                TaskModel.closed_at.is_not(None),
                TaskModel.completed_at.is_not(None),
            )
            .returning(TaskModel)
        )

        return list(result.scalars().all())

    async def delete_close_user_tasks(self, user_id: UUID) -> list[TaskModel]:
        result = await self._async_session.execute(
            delete(TaskModel)
            .where(TaskModel.user_id == user_id, TaskModel.closed_at.is_not(None))
            .returning(TaskModel)
        )

        return list(result.scalars().all())

    async def delete_complete_user_tasks(self, user_id: UUID) -> list[TaskModel]:
        result = await self._async_session.execute(
            delete(TaskModel)
            .where(TaskModel.user_id == user_id, TaskModel.completed_at.is_not(None))
            .returning(TaskModel)
        )

        return list(result.scalars().all())

    async def alter_close_user_task(self, user_id: UUID, task_id: UUID) -> TaskModel | None:
        result = await self._async_session.execute(
            update(TaskModel)
            .where(
                TaskModel.task_id == task_id,
                TaskModel.user_id == user_id,
                TaskModel.closed_at.is_(None),
            )
            .values(closed_at=datetime.now(UTC))
            .returning(TaskModel)
        )

        return result.scalar_one_or_none()

    async def alter_complete_user_task(self, user_id: UUID, task_id: UUID) -> TaskModel | None:
        result = await self._async_session.execute(
            update(TaskModel)
            .where(
                TaskModel.task_id == task_id,
                TaskModel.user_id == user_id,
                TaskModel.completed_at.is_(None),
            )
            .values(completed_at=datetime.now(UTC))
            .returning(TaskModel)
        )

        return result.scalar_one_or_none()

    async def alter_user_task_params(
        self, user_id: UUID, task_id: UUID, new_params: dict
    ) -> TaskModel | None:
        result = await self._async_session.execute(
            update(TaskModel)
            .where(TaskModel.user_id == user_id, TaskModel.task_id == task_id)
            .values(**new_params)
            .returning(TaskModel)
        )

        return result.scalar_one_or_none()
