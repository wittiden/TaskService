from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.common.enums.task import TaskImportantLevelEnum, TaskScheduleEnum
from app.common.enums.user import UserRoleEnum
from app.modules.audits.service.use_cases import CreateTaskAuditCase
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

    def __init__(
        self,
        task_commands: TaskCommandsRepository,
        task_queries: TaskQueriesRepository,
        create_task_audit_case: CreateTaskAuditCase,
    ) -> None:
        self._task_commands = task_commands
        self._task_queries = task_queries
        self._create_task_audit_case = create_task_audit_case

    async def update_my_task_params(
        self, user_id: UUID, task_id: UUID, new_params: dict
    ) -> FullTaskInfoDTO:
        columns = await self._task_queries.select_user_task_close_complete_params(user_id, task_id)
        columns = TaskGuards.require_task_columns_exist(columns)

        TaskGuards.require_task_not_closed(columns)
        TaskGuards.require_task_not_completed(columns)

        result = await self._task_commands.alter_user_task_params(user_id, task_id, new_params)
        result = TaskGuards.require_task_exist(result)

        for key, value in new_params.items():
            old_value = columns.get(key)
            await self._create_task_audit_case.create_task_audit(
                task_id, key, new_value=str(value), old_value=str(old_value)
            )

        return FullTaskInfoDTO.model_validate(result)


class DeleteTaskCase:
    """Кейс по удалению задач"""

    def __init__(self, task_commands: TaskCommandsRepository) -> None:
        self._task_commands = task_commands

    async def delete_user_task_by_id(self, task_id: UUID, user_id: UUID) -> None:
        result = await self._task_commands.delete_user_task_by_id(task_id, user_id)
        TaskGuards.require_deleted_task_exist(result)

    async def delete_user_tasks(self, user_id: UUID) -> None:
        result = await self._task_commands.delete_user_tasks(user_id)
        TaskGuards.require_deleted_tasks_exist(result)

    async def delete_close_complete_user_tasks(self, user_id: UUID) -> None:
        result = await self._task_commands.delete_close_complete_user_tasks(user_id)
        TaskGuards.require_deleted_tasks_exist(result)

    async def delete_close_user_tasks(self, user_id: UUID) -> None:
        result = await self._task_commands.delete_close_user_tasks(user_id)
        TaskGuards.require_deleted_tasks_exist(result)

    async def delete_complete_user_tasks(self, user_id: UUID) -> None:
        result = await self._task_commands.delete_complete_user_tasks(user_id)
        TaskGuards.require_deleted_tasks_exist(result)


class ManageTaskCase:
    """Класс по менедженгу задач"""

    def __init__(
        self, task_commands: TaskCommandsRepository, create_task_audit_case: CreateTaskAuditCase
    ) -> None:
        self._task_commands = task_commands
        self._create_task_audit_case = create_task_audit_case

    async def close_my_task(self, user_id: UUID, task_id: UUID) -> FullTaskInfoDTO:
        result = await self._task_commands.alter_close_user_task(user_id, task_id)
        result = TaskGuards.require_task_with_spec_params_exist(result)

        await self._create_task_audit_case.create_task_audit(
            task_id, 'closed_at', None, new_value=str(result.closed_at)
        )
        return FullTaskInfoDTO.model_validate(result)

    async def complete_my_task(self, user_id: UUID, task_id: UUID) -> FullTaskInfoDTO:
        result = await self._task_commands.alter_complete_user_task(user_id, task_id)
        result = TaskGuards.require_task_with_spec_params_exist(result)

        await self._create_task_audit_case.create_task_audit(
            task_id, 'completed_at', None, new_value=str(result.completed_at)
        )
        return FullTaskInfoDTO.model_validate(result)


class ShowTaskCase:
    """Кейс по показу задач"""

    def __init__(self, task_queries: TaskQueriesRepository) -> None:
        self._task_queries = task_queries

    async def show_user_task_by_id(self, task_id: UUID, user_id: UUID) -> FullTaskInfoDTO:
        task = await self._task_queries.select_user_task_by_id(task_id, user_id)
        task = TaskGuards.require_task_exist(task)
        return FullTaskInfoDTO.model_validate(task)

    async def show_user_tasks(
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
