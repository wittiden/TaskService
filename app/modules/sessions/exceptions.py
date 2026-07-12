from app.common.exceptions.base_exception import RouterError


class SessionRouterError(RouterError):
    title = 'Session router error'
    status_code = 400


class RefreshTokenNotFoundError(SessionRouterError):
    title = 'Refresh token not found error'
    status_code = 404
