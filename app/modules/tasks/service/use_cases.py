from uuid import UUID

from contracts.dtos import FullTaskInfoDTO, SecurityTaskInfoDTO
from exceptions import TaskInvalidDataError
from repository.commands import TaskCommandsRepository
from repository.queries import TaskQueriesRepository
from service.guards import TaskGuards
from sqlalchemy.exc import IntegrityError

from app.common.enums.task import TaskImportantLevelEnum, TaskScheduleEnum


class CreateTaskCase:
    """Кейс по созданию задач"""

    def __init__(self, task_commands: TaskCommandsRepository) -> None:
        self._task_commands = task_commands

    async def create_task(
        self,
        user_id: UUID,
        important_level: TaskImportantLevelEnum,
        schedule_type: TaskScheduleEnum,
        title: str,
        description: str | None,
    ):
        try:
            task = await self._task_commands.insert_task(
                user_id, important_level, schedule_type, title, description
            )
        except IntegrityError as exc:
            raise TaskInvalidDataError(str(exc)) from exc

        task = TaskGuards.require_create_task_exist(task)

        return task


class UpdateTaskCase:
    """Кейс по обновлению данных задач"""


class DeleteTaskCase:
    """Кейс по удалению задач"""


class ShowTaskCase:
    """Кейс по показу задач"""

    def __init__(self, task_queries: TaskQueriesRepository) -> None:
        self._task_queries = task_queries

    async def show_tasks(self, offset: int = 0, limit: int = 100) -> list[FullTaskInfoDTO]:
        tasks = await self._task_queries.select_tasks(offset, limit)
        return [FullTaskInfoDTO.model_validate(task) for task in tasks]

    async def show_task_by_id(self, task_id: UUID) -> FullTaskInfoDTO:
        task = await self._task_queries.select_task_by_id(task_id)
        task = TaskGuards.require_task_exist(task)
        return FullTaskInfoDTO.model_validate(task)

    async def show_tasks_by_user_id(
        self, user_id: UUID, offset: int = 0, limit: int = 100
    ) -> list[SecurityTaskInfoDTO]:
        tasks = await self._task_queries.select_tasks_by_user_id(user_id, offset, limit)
        return [SecurityTaskInfoDTO.model_validate(task) for task in tasks]

    async def show_user_completed_tasks(
        self, user_id: UUID, offset: int = 0, limit: int = 100
    ) -> list[SecurityTaskInfoDTO]:
        tasks = await self._task_queries.select_user_completed_tasks(user_id, offset, limit)
        return [SecurityTaskInfoDTO.model_validate(task) for task in tasks]

    async def show_user_closed_tasks(
        self, user_id: UUID, offset: int = 0, limit: int = 100
    ) -> list[SecurityTaskInfoDTO]:
        tasks = await self._task_queries.select_user_closed_tasks(user_id, offset, limit)
        return [SecurityTaskInfoDTO.model_validate(task) for task in tasks]

    async def show_user_active_tasks(
        self, user_id: UUID, offset: int = 0, limit: int = 100
    ) -> list[SecurityTaskInfoDTO]:
        tasks = await self._task_queries.select_user_active_tasks(user_id, offset, limit)
        return [SecurityTaskInfoDTO.model_validate(task) for task in tasks]
