from app.common.exceptions.base_ex import RouterError


class HealthRouterError(RouterError):
    status_code = 500
    title = 'Health router error'


class AppHealthError(HealthRouterError):
    status_code = 500
    title = 'Application healthcheck error'


class DbHealthError(HealthRouterError):
    status_code = 500
    title = 'Database healthcheck error'


class RedisHealthError(HealthRouterError):
    status_code = 500
    title = 'Redis healthcheck error'
