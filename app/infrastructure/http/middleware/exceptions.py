from app.common.exceptions.base_ex import RouterError


class MiddlewareRouterError(RouterError):
    status_code = 400
    title = 'Middleware router error'


class HTTPTimeoutError(MiddlewareRouterError):
    status_code = 504
    title = 'HTTP timeout error'
