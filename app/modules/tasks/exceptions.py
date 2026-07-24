from app.common.exceptions.base_exception import RouterError


class TaskRouterError(RouterError):
    title = 'Task router error'
    status_code = 400


class TaskInvalidDataError(TaskRouterError):
    title = 'Task invalid data error'
    status_code = 400


class TaskNotFoundError(TaskRouterError):
    title = 'Task not found error'
    status_code = 404


class TaskLimitError(TaskRouterError):
    title = 'Task limit error'
    status_code = 409
