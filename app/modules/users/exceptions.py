from app.common.exceptions.base_ex import RouterError


class UserRouterError(RouterError):
    status_code = 400
    title = 'User router error'


class EmailIsExistError(UserRouterError):
    status_code = 409
    title = 'Email is exist error'


class InvalidPassError(UserRouterError):
    status_code = 401
    title = 'Invalid password error'


class UserNotFoundError(UserRouterError):
    status_code = 404
    title = 'User not found error'
