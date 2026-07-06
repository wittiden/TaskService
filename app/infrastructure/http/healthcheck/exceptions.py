from app.common.exceptions.base_exception import RouterError


class HealthRouterError(RouterError):
    title = 'Health router error'
    status_code = 400


class ApplicationHealthError(HealthRouterError):
    title = 'Application health error'
    status_code = 500


class DatabaseHealthError(HealthRouterError):
    title = 'Database health error'
    status_code = 500


class RedisHealthError(HealthRouterError):
    title = 'Redis health error'
    status_code = 500
