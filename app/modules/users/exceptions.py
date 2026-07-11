from app.common.exceptions.base_exception import RouterError


class UserRouterError(RouterError):
    title = 'Router error'
    status_code = 400


class InvalidUserDataError(UserRouterError):
    title = 'Invalid user data error'
    status_code = 400


class UserColumnsNotFoundError(UserRouterError):
    title = 'User columns not found error'
    status_code = 404


class UserBlockedError(UserRouterError):
    title = 'User blocked error'
    status_code = 401


class UserClosedError(UserRouterError):
    title = 'User closed error'
    status_code = 401


class UserNotFoundError(UserRouterError):
    title = 'User not found error'
    status_code = 404


class UserAlreadyBlockedError(UserRouterError):
    title = 'User already blocked error'
    status_code = 409


class UserAlreadyUnblockedError(UserRouterError):
    title = 'User already unblocked error'
    status_code = 409
