from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.common.enums.task import TaskImportantLevelEnum, TaskScheduleEnum
from app.common.enums.user import UserRoleEnum
from app.modules.tasks.config import TaskConfig
from app.modules.tasks.contracts.dtos import FullTaskInfoDTO, SecurityTaskInfoDTO
from app.modules.tasks.exceptions import TaskInvalidDataError, TaskLimitError
from app.modules.tasks.repository.commands import TaskCommandsRepository
from app.modules.tasks.repository.queries import TaskQueriesRepository
from app.modules.tasks.service.guards import TaskGuards
from app.modules.users.contracts.dtos import FullUserInfoDTO


class CreateTaskCase:
    """Кейс по созданию задач"""

    def __init__(
        self,
        task_commands: TaskCommandsRepository,
        task_config: TaskConfig,
        task_queries: TaskQueriesRepository,
    ) -> None:
        self._task_commands = task_commands
        self._task_config = task_config
        self._task_queries = task_queries

    async def create_task(
        self,
        current_user: FullUserInfoDTO,
        important_level: TaskImportantLevelEnum,
        schedule_type: TaskScheduleEnum,
        title: str,
        description: str | None,
    ) -> SecurityTaskInfoDTO:

        count = await self._task_queries.select_user_tasks_count(current_user.user_id)
        if (
            current_user.role == UserRoleEnum.STANDARD
            and count > self._task_config.STANDARD_TASK_COUNT_LIMIT
        ):
            raise TaskLimitError(
                f'Tasks limit for standard user = {self._task_config.STANDARD_TASK_COUNT_LIMIT}'
            )
        elif (
            current_user.role == UserRoleEnum.VIP and count > self._task_config.VIP_TASK_COUNT_LIMIT
        ):
            raise TaskLimitError(
                f'Tasks limit for vip user = {self._task_config.VIP_TASK_COUNT_LIMIT}'
            )

        try:
            task = await self._task_commands.insert_task(
                current_user.user_id, important_level, schedule_type, title, description
            )
        except IntegrityError as exc:
            raise TaskInvalidDataError(str(exc)) from exc

        task = TaskGuards.require_create_task_exist(task)

        return SecurityTaskInfoDTO.model_validate(task)


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
