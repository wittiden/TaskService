from app.common.exceptions.base_exception import RouterError


class UserAuditRouterError(RouterError):
    title = 'User audit router error'
    status_code = 400


class UserAuditModelIntegrityError(UserAuditRouterError):
    title = 'User audit model integrity error'
    status_code = 409


class UserAuditNotFoundError(UserAuditRouterError):
    title = 'User audit not found error'
    status_code = 404
