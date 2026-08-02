from loguru import logger

from app.infrastructure.database.model import TaskModel
from app.modules.tasks.exceptions import (
    ClosedTaskError,
    CompletedTaskError,
    TaskInvalidDataError,
    TaskNotFoundError,
)


class TaskGuards:
    """Класс бизнес правил задач"""

    @staticmethod
    def require_create_task_exist(task: TaskModel | None) -> TaskModel:
        if task is None:
            logger.warning('Task cant created - TaskInvalidDataError')
            raise TaskInvalidDataError('Task cant created due to invalid data')

        return task

    @staticmethod
    def require_task_exist(task: TaskModel | None) -> TaskModel:
        if task is None:
            logger.warning('Empty task - TaskNotFoundError')
            raise TaskNotFoundError('Task obj is empty')

        return task

    @staticmethod
    def require_deleted_task_exist(deleted_task: TaskModel | None) -> None:
        if deleted_task is None:
            logger.warning('Task obj cant found for deletion - TaskNotFoundError')
            raise TaskNotFoundError('Task obj cant found for deletion')

    @staticmethod
    def require_deleted_tasks_exist(deleted_task: list[TaskModel]) -> None:
        if not deleted_task:
            logger.warning('Tasks objs cant found for deletion - TaskNotFoundError')
            raise TaskNotFoundError('Tasks objs cant found for deletion')

    @staticmethod
    def require_task_with_spec_params_exist(task: TaskModel | None) -> TaskModel:
        if task is None:
            logger.warning('Task with spec params not found - TaskNotFoundError')
            raise TaskNotFoundError('Your task with spec params not found')

        return task

    @staticmethod
    def require_task_columns_exist(columns: dict | None) -> dict:
        if columns is None:
            logger.warning('Task columns not found by id - TaskNotFoundError')
            raise TaskNotFoundError('Task columns not found by id')

        return columns

    @staticmethod
    def require_task_not_completed(columns: dict) -> None:
        if columns['completed_at'] is not None:
            logger.warning('Task already completed - CompletedTaskError')
            raise CompletedTaskError('This task already completed, you cant change it')

    @staticmethod
    def require_task_not_closed(columns: dict) -> None:
        if columns['closed_at'] is not None:
            logger.warning('Task already closed - ClosedTaskError')
            raise ClosedTaskError('This task already closed, you cant change it')
