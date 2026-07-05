from app.common.exceptions.base_exception import RouterError


class HealthRouterError(RouterError):
    title = 'Health router error'
    status_code = 400


class ApplicationError(HealthRouterError):
    title = 'Application error'
    status_code = 500


class DatabaseError(HealthRouterError):
    title = 'Database error'
    status_code = 500


class RedisError(HealthRouterError):
    title = 'Redis error'
    status_code = 500
