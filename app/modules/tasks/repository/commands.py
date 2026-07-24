from uuid import UUID

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
