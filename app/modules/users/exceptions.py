from app.common.security.base_exception import RouterError


class UserRouterError(RouterError):
    title = 'Router error'
    status_code = 400


class PassVerifyError(UserRouterError):
    title = 'Pass verify error'
    status_code = 401


class InvalidUserDataError(UserRouterError):
    title = 'Invalid user data error'
    status_code = 400
