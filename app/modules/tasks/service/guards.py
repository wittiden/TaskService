from exceptions import TaskInvalidDataError, TaskNotFoundError

from app.infrastructure.database.model import TaskModel


class TaskGuards:
    """Класс бизнес правил задач"""

    @staticmethod
    def require_create_task_exist(task: TaskModel | None) -> TaskModel:
        if task is None:
            raise TaskInvalidDataError('Task cant created due to invalid data')

        return task

    @staticmethod
    def require_task_exist(task: TaskModel | None) -> TaskModel:
        if task is None:
            raise TaskNotFoundError('Task obj is empty')

        return task
