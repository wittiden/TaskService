from uuid import UUID

from loguru import logger
from sqlalchemy.exc import IntegrityError

from app.modules.audits.contracts.dtos import FullTaskAuditInfoDTO, FullUserAuditInfoDTO
from app.modules.audits.exceptions import TaskAuditModelIntegrityError, UserAuditModelIntegrityError
from app.modules.audits.repository.commands import (
    TaskAuditCommandsRepository,
    UserAuditCommandsRepository,
)
from app.modules.audits.repository.queries import (
    TaskAuditQueriesRepository,
    UserAuditQueriesRepository,
)
from app.modules.audits.service.guards import AuditGuards


class CreateUserAuditCase:
    """Кейс по созданию аудита пользователя"""

    __slots__ = ('_user_audit_commands',)

    def __init__(self, user_audit_commands: UserAuditCommandsRepository):
        self._user_audit_commands = user_audit_commands

    async def create_user_audit(
        self,
        user_id: UUID,
        field_name: str,
        old_value: str | None,
        new_value: str | None,
    ) -> None:
        logger.debug(
            'Creating user audit entry',
            extra={
                'user_id': str(user_id),
                'field_name': field_name,
                'old_value': old_value if old_value else '*****',
                'new_value': new_value if new_value else '*****',
            },
        )

        try:
            await self._user_audit_commands.insert_user_audit_obj(
                user_id, field_name, old_value, new_value
            )

            logger.debug(
                'User audit entry created successfully',
                extra={
                    'user_id': str(user_id),
                    'field_name': field_name,
                },
            )

        except IntegrityError as exc:
            logger.warning(
                'User audit creation failed - integrity error',
                extra={
                    'user_id': str(user_id),
                    'field_name': field_name,
                    'error': str(exc),
                },
            )
            raise UserAuditModelIntegrityError(str(exc)) from exc


class CreateTaskAuditCase:
    """Кейс по созданию аудита задач"""

    __slots__ = ('_task_audit_commands',)

    def __init__(self, task_audit_commands: TaskAuditCommandsRepository) -> None:
        self._task_audit_commands = task_audit_commands

    async def create_task_audit(
        self, task_id: UUID, field_name: str, old_value: str | None, new_value: str | None
    ) -> None:
        logger.debug(
            'Creating task audit entry',
            extra={
                'task_id': str(task_id),
                'field_name': field_name,
                'old_value': old_value if old_value else '*****',
                'new_value': new_value if new_value else '*****',
            },
        )

        try:
            await self._task_audit_commands.insert_task_audit_obj(
                task_id, field_name, old_value, new_value
            )

            logger.debug(
                'Task audit entry created successfully',
                extra={
                    'task_id': str(task_id),
                    'field_name': field_name,
                },
            )

        except IntegrityError as exc:
            logger.warning(
                'Task audit creation failed - integrity error',
                extra={
                    'task_id': str(task_id),
                    'field_name': field_name,
                    'error': str(exc),
                },
            )
            raise TaskAuditModelIntegrityError(str(exc)) from exc


class ShowUserAuditCase:
    """Кейс по показу информации аудита пользователя"""

    __slots__ = ('_user_audit_queries',)

    def __init__(self, user_audit_queries: UserAuditQueriesRepository) -> None:
        self._user_audit_queries = user_audit_queries

    async def show_user_audits(
        self, offset: int = 0, limit: int = 100
    ) -> list[FullUserAuditInfoDTO]:
        logger.debug(
            'Showing user audits',
            extra={
                'offset': offset,
                'limit': limit,
            },
        )

        objs = await self._user_audit_queries.select_user_audits(offset, limit)

        logger.info(
            'User audits retrieved',
            extra={
                'count': len(objs),
                'offset': offset,
                'limit': limit,
            },
        )
        return [FullUserAuditInfoDTO.model_validate(obj) for obj in objs]

    async def show_user_audits_by_user_id(
        self, user_id: UUID, offset: int = 0, limit: int = 100
    ) -> list[FullUserAuditInfoDTO]:
        logger.debug(
            'Showing user audits by user ID',
            extra={
                'user_id': str(user_id),
                'offset': offset,
                'limit': limit,
            },
        )

        objs = await self._user_audit_queries.select_user_audits_by_user_id(user_id, offset, limit)

        logger.info(
            'User audits by user ID retrieved',
            extra={
                'user_id': str(user_id),
                'count': len(objs),
                'offset': offset,
                'limit': limit,
            },
        )
        return [FullUserAuditInfoDTO.model_validate(obj) for obj in objs]

    async def show_user_audit_by_id(self, user_audit_id: UUID) -> FullUserAuditInfoDTO:
        logger.debug('Showing user audit by ID', extra={'user_audit_id': str(user_audit_id)})

        obj = await self._user_audit_queries.select_user_audit_by_id(user_audit_id)
        obj = AuditGuards.require_user_audit_exist(obj)

        logger.info(
            'User audit found by ID',
            extra={
                'user_audit_id': str(user_audit_id),
                'user_id': str(obj.user_id),
                'field_name': obj.field_name,
                'old_value': obj.old_value if obj.old_value else 'None',
                'new_value': obj.new_value if obj.new_value else 'None',
            },
        )
        return FullUserAuditInfoDTO.model_validate(obj)


class ShowTaskAuditCase:
    """Кейс по показу информации аудита задач"""

    __slots__ = ('_task_audit_queries',)

    def __init__(self, task_audit_queries: TaskAuditQueriesRepository) -> None:
        self._task_audit_queries = task_audit_queries

    async def show_task_audits(
        self, offset: int = 0, limit: int = 100
    ) -> list[FullTaskAuditInfoDTO]:
        logger.debug(
            'Showing task audits',
            extra={
                'offset': offset,
                'limit': limit,
            },
        )

        task_audits = await self._task_audit_queries.select_task_audits(offset, limit)

        logger.info(
            'Task audits retrieved',
            extra={
                'count': len(task_audits),
                'offset': offset,
                'limit': limit,
            },
        )
        return [FullTaskAuditInfoDTO.model_validate(task_audit) for task_audit in task_audits]

    async def show_task_audit_by_id(self, task_audit_id: UUID) -> FullTaskAuditInfoDTO:
        logger.debug('Showing task audit by ID', extra={'task_audit_id': str(task_audit_id)})

        task_audit = await self._task_audit_queries.select_task_audit_by_id(task_audit_id)
        task_audit = AuditGuards.require_task_audit_exist(task_audit)

        logger.info(
            'Task audit found by ID',
            extra={
                'task_audit_id': str(task_audit_id),
                'task_id': str(task_audit.task_id),
                'field_name': task_audit.field_name,
                'old_value': task_audit.old_value if task_audit.old_value else 'None',
                'new_value': task_audit.new_value if task_audit.new_value else 'None',
            },
        )
        return FullTaskAuditInfoDTO.model_validate(task_audit)

    async def show_task_audits_by_task_id(
        self, task_id: UUID, offset: int = 0, limit: int = 100
    ) -> list[FullTaskAuditInfoDTO]:
        logger.debug(
            'Showing task audits by task ID',
            extra={
                'task_id': str(task_id),
                'offset': offset,
                'limit': limit,
            },
        )

        task_audits = await self._task_audit_queries.select_task_audits_by_task_id(
            task_id, offset, limit
        )

        logger.info(
            'Task audits by task ID retrieved',
            extra={
                'task_id': str(task_id),
                'count': len(task_audits),
                'offset': offset,
                'limit': limit,
            },
        )
        return [FullTaskAuditInfoDTO.model_validate(task_audit) for task_audit in task_audits]
