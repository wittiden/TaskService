from uuid import UUID

from loguru import logger
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

    __slots__ = ('_task_commands', '_task_config', '_task_queries')

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
        logger.debug(
            'Creating task',
            extra={
                'user_id': str(current_user.user_id),
                'email': current_user.email,
                'important_level': important_level.value,
                'schedule_type': schedule_type.value,
                'title': title,
            },
        )

        count = await self._task_queries.select_user_tasks_count(current_user.user_id)
        if (
            current_user.role == UserRoleEnum.STANDARD
            and count > self._task_config.STANDARD_TASK_COUNT_LIMIT
        ):
            logger.warning(
                'Task limit exceeded for standard user',
                extra={
                    'user_id': str(current_user.user_id),
                    'count': count,
                    'limit': self._task_config.STANDARD_TASK_COUNT_LIMIT,
                },
            )
            raise TaskLimitError(
                f'Tasks limit for standard user = {self._task_config.STANDARD_TASK_COUNT_LIMIT}'
            )
        elif (
            current_user.role == UserRoleEnum.VIP and count > self._task_config.VIP_TASK_COUNT_LIMIT
        ):
            logger.warning(
                'Task limit exceeded for VIP user',
                extra={
                    'user_id': str(current_user.user_id),
                    'count': count,
                    'limit': self._task_config.VIP_TASK_COUNT_LIMIT,
                },
            )
            raise TaskLimitError(
                f'Tasks limit for vip user = {self._task_config.VIP_TASK_COUNT_LIMIT}'
            )

        try:
            task = await self._task_commands.insert_task(
                current_user.user_id, important_level, schedule_type, title, description
            )
        except IntegrityError as exc:
            logger.warning(
                'Task creation failed - integrity error',
                extra={
                    'user_id': str(current_user.user_id),
                    'error': str(exc),
                },
            )
            raise TaskInvalidDataError(str(exc)) from exc

        task = TaskGuards.require_create_task_exist(task)

        logger.info(
            'Task created successfully',
            extra={
                'task_id': str(task.task_id),
                'user_id': str(current_user.user_id),
                'important_level': task.important_level.value,
                'schedule_type': task.schedule_type.value,
                'title': task.title,
            },
        )
        return SecurityTaskInfoDTO.model_validate(task)


class UpdateTaskCase:
    """Кейс по обновлению данных задач"""

    __slots__ = ('_create_task_audit_case', '_task_commands', '_task_queries')

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
        logger.debug(
            'Updating task parameters',
            extra={
                'user_id': str(user_id),
                'task_id': str(task_id),
                'new_params': new_params,
            },
        )

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

        logger.info(
            'Task updated successfully',
            extra={
                'task_id': str(task_id),
                'user_id': str(user_id),
                'updated_fields': list(new_params.keys()),
            },
        )
        return FullTaskInfoDTO.model_validate(result)


class DeleteTaskCase:
    """Кейс по удалению задач"""

    __slots__ = ('_task_commands',)

    def __init__(self, task_commands: TaskCommandsRepository) -> None:
        self._task_commands = task_commands

    async def delete_user_task_by_id(self, task_id: UUID, user_id: UUID) -> None:
        logger.debug(
            'Deleting task by ID',
            extra={
                'task_id': str(task_id),
                'user_id': str(user_id),
            },
        )

        result = await self._task_commands.delete_user_task_by_id(task_id, user_id)
        TaskGuards.require_deleted_task_exist(result)

        logger.info(
            'Task deleted successfully',
            extra={
                'task_id': str(task_id),
                'user_id': str(user_id),
            },
        )

    async def delete_user_tasks(self, user_id: UUID) -> None:
        logger.debug('Deleting all user tasks', extra={'user_id': str(user_id)})

        result = await self._task_commands.delete_user_tasks(user_id)
        TaskGuards.require_deleted_tasks_exist(result)

        logger.info('All user tasks deleted', extra={'user_id': str(user_id)})

    async def delete_close_complete_user_tasks(self, user_id: UUID) -> None:
        logger.debug('Deleting closed and completed user tasks', extra={'user_id': str(user_id)})

        result = await self._task_commands.delete_close_complete_user_tasks(user_id)
        TaskGuards.require_deleted_tasks_exist(result)

        logger.info('Closed and completed tasks deleted', extra={'user_id': str(user_id)})

    async def delete_close_user_tasks(self, user_id: UUID) -> None:
        logger.debug('Deleting closed user tasks', extra={'user_id': str(user_id)})

        result = await self._task_commands.delete_close_user_tasks(user_id)
        TaskGuards.require_deleted_tasks_exist(result)

        logger.info('Closed tasks deleted', extra={'user_id': str(user_id)})

    async def delete_complete_user_tasks(self, user_id: UUID) -> None:
        logger.debug('Deleting completed user tasks', extra={'user_id': str(user_id)})

        result = await self._task_commands.delete_complete_user_tasks(user_id)
        TaskGuards.require_deleted_tasks_exist(result)

        logger.info('Completed tasks deleted', extra={'user_id': str(user_id)})


class ManageTaskCase:
    """Класс по менедженгу задач"""

    __slots__ = ('_create_task_audit_case', '_task_commands')

    def __init__(
        self, task_commands: TaskCommandsRepository, create_task_audit_case: CreateTaskAuditCase
    ) -> None:
        self._task_commands = task_commands
        self._create_task_audit_case = create_task_audit_case

    async def close_my_task(self, user_id: UUID, task_id: UUID) -> FullTaskInfoDTO:
        logger.debug(
            'Closing task',
            extra={
                'user_id': str(user_id),
                'task_id': str(task_id),
            },
        )

        result = await self._task_commands.alter_close_user_task(user_id, task_id)
        result = TaskGuards.require_task_with_spec_params_exist(result)

        await self._create_task_audit_case.create_task_audit(
            task_id, 'closed_at', None, new_value=str(result.closed_at)
        )

        logger.info(
            'Task closed successfully',
            extra={
                'task_id': str(task_id),
                'user_id': str(user_id),
                'closed_at': str(result.closed_at),
            },
        )
        return FullTaskInfoDTO.model_validate(result)

    async def complete_my_task(self, user_id: UUID, task_id: UUID) -> FullTaskInfoDTO:
        logger.debug(
            'Completing task',
            extra={
                'user_id': str(user_id),
                'task_id': str(task_id),
            },
        )

        result = await self._task_commands.alter_complete_user_task(user_id, task_id)
        result = TaskGuards.require_task_with_spec_params_exist(result)

        await self._create_task_audit_case.create_task_audit(
            task_id, 'completed_at', None, new_value=str(result.completed_at)
        )

        logger.info(
            'Task completed successfully',
            extra={
                'task_id': str(task_id),
                'user_id': str(user_id),
                'completed_at': str(result.completed_at),
            },
        )
        return FullTaskInfoDTO.model_validate(result)


class ShowTaskCase:
    """Кейс по показу задач"""

    __slots__ = ('_task_queries',)

    def __init__(self, task_queries: TaskQueriesRepository) -> None:
        self._task_queries = task_queries

    async def show_user_task_by_id(self, task_id: UUID, user_id: UUID) -> FullTaskInfoDTO:
        logger.debug(
            'Showing task by ID',
            extra={
                'task_id': str(task_id),
                'user_id': str(user_id),
            },
        )

        task = await self._task_queries.select_user_task_by_id(task_id, user_id)
        task = TaskGuards.require_task_exist(task)

        logger.info(
            'Task found by ID',
            extra={
                'task_id': str(task_id),
                'user_id': str(user_id),
                'title': task.title,
                'important_level': task.important_level,
            },
        )
        return FullTaskInfoDTO.model_validate(task)

    async def show_user_tasks(
        self, user_id: UUID, offset: int = 0, limit: int = 100
    ) -> list[SecurityTaskInfoDTO]:
        logger.debug(
            'Showing user tasks',
            extra={
                'user_id': str(user_id),
                'offset': offset,
                'limit': limit,
            },
        )

        tasks = await self._task_queries.select_tasks_by_user_id(user_id, offset, limit)

        logger.info(
            'User tasks retrieved',
            extra={
                'user_id': str(user_id),
                'count': len(tasks),
                'offset': offset,
                'limit': limit,
            },
        )
        return [SecurityTaskInfoDTO.model_validate(task) for task in tasks]

    async def show_user_completed_tasks(
        self, user_id: UUID, offset: int = 0, limit: int = 100
    ) -> list[SecurityTaskInfoDTO]:
        logger.debug(
            'Showing user completed tasks',
            extra={
                'user_id': str(user_id),
                'offset': offset,
                'limit': limit,
            },
        )

        tasks = await self._task_queries.select_user_completed_tasks(user_id, offset, limit)

        logger.info(
            'User completed tasks retrieved',
            extra={
                'user_id': str(user_id),
                'count': len(tasks),
                'offset': offset,
                'limit': limit,
            },
        )
        return [SecurityTaskInfoDTO.model_validate(task) for task in tasks]

    async def show_user_closed_tasks(
        self, user_id: UUID, offset: int = 0, limit: int = 100
    ) -> list[SecurityTaskInfoDTO]:
        logger.debug(
            'Showing user closed tasks',
            extra={
                'user_id': str(user_id),
                'offset': offset,
                'limit': limit,
            },
        )

        tasks = await self._task_queries.select_user_closed_tasks(user_id, offset, limit)

        logger.info(
            'User closed tasks retrieved',
            extra={
                'user_id': str(user_id),
                'count': len(tasks),
                'offset': offset,
                'limit': limit,
            },
        )
        return [SecurityTaskInfoDTO.model_validate(task) for task in tasks]

    async def show_user_active_tasks(
        self, user_id: UUID, offset: int = 0, limit: int = 100
    ) -> list[SecurityTaskInfoDTO]:
        logger.debug(
            'Showing user active tasks',
            extra={
                'user_id': str(user_id),
                'offset': offset,
                'limit': limit,
            },
        )

        tasks = await self._task_queries.select_user_active_tasks(user_id, offset, limit)

        logger.info(
            'User active tasks retrieved',
            extra={
                'user_id': str(user_id),
                'count': len(tasks),
                'offset': offset,
                'limit': limit,
            },
        )
        return [SecurityTaskInfoDTO.model_validate(task) for task in tasks]
