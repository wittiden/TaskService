from uuid import UUID

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

    def __init__(self, user_audit_commands: UserAuditCommandsRepository):
        self._user_audit_commands = user_audit_commands

    async def create_user_audit(
        self,
        user_id: UUID,
        field_name: str,
        old_value: str | None,
        new_value: str | None,
    ) -> None:
        try:
            await self._user_audit_commands.insert_user_audit_obj(
                user_id, field_name, old_value, new_value
            )

        except IntegrityError as exc:
            raise UserAuditModelIntegrityError(str(exc)) from exc


class CreateTaskAuditCase:
    """Кейс по созданию аудита задач"""

    def __init__(self, task_audit_commands: TaskAuditCommandsRepository) -> None:
        self._task_audit_commands = task_audit_commands

    async def create_task_audit(
        self, task_id: UUID, field_name: str, old_value: str | None, new_value: str | None
    ) -> None:
        try:
            await self._task_audit_commands.insert_task_audit_obj(
                task_id, field_name, old_value, new_value
            )
        except IntegrityError as exc:
            raise TaskAuditModelIntegrityError(str(exc)) from exc


class ShowUserAuditCase:
    """Кейс по показу информации аудита пользователя"""

    def __init__(self, user_audit_queries: UserAuditQueriesRepository) -> None:
        self._user_audit_queries = user_audit_queries

    async def show_user_audits(
        self, offset: int = 0, limit: int = 100
    ) -> list[FullUserAuditInfoDTO]:
        objs = await self._user_audit_queries.select_user_audits(offset, limit)
        return [FullUserAuditInfoDTO.model_validate(obj) for obj in objs]

    async def show_user_audits_by_user_id(
        self, user_id: UUID, offset: int = 0, limit: int = 100
    ) -> list[FullUserAuditInfoDTO]:
        objs = await self._user_audit_queries.select_user_audits_by_user_id(user_id, offset, limit)
        return [FullUserAuditInfoDTO.model_validate(obj) for obj in objs]

    async def show_user_audit_by_id(self, user_audit_id: UUID) -> FullUserAuditInfoDTO:
        obj = await self._user_audit_queries.select_user_audit_by_id(user_audit_id)
        obj = AuditGuards.require_user_audit_exist(obj)

        return FullUserAuditInfoDTO.model_validate(obj)


class ShowTaskAuditCase:
    """Кейс по показу информации аудита задач"""

    def __init__(self, task_audit_queries: TaskAuditQueriesRepository) -> None:
        self._task_audit_queries = task_audit_queries

    async def show_task_audits(
        self, offset: int = 0, limit: int = 100
    ) -> list[FullTaskAuditInfoDTO]:
        task_audits = await self._task_audit_queries.select_task_audits(offset, limit)
        return [FullTaskAuditInfoDTO.model_validate(task_audit) for task_audit in task_audits]

    async def show_task_audit_by_id(self, task_audit_id: UUID) -> FullTaskAuditInfoDTO:
        task_audit = await self._task_audit_queries.select_task_audit_by_id(task_audit_id)
        task_audit = AuditGuards.require_task_audit_exist(task_audit)
        return FullTaskAuditInfoDTO.model_validate(task_audit)

    async def show_task_audits_by_task_id(
        self, task_id: UUID, offset: int = 0, limit: int = 100
    ) -> list[FullTaskAuditInfoDTO]:
        task_audits = await self._task_audit_queries.select_task_audits_by_task_id(
            task_id, offset, limit
        )
        return [FullTaskAuditInfoDTO.model_validate(task_audit) for task_audit in task_audits]
