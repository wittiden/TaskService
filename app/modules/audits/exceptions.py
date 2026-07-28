from app.common.exceptions.base_exception import RouterError


class AuditRouterError(RouterError):
    title = 'User audits router error'
    status_code = 400


class UserAuditModelIntegrityError(AuditRouterError):
    title = 'User audits model integrity error'
    status_code = 409


class TaskAuditModelIntegrityError(AuditRouterError):
    title = 'Task audits model integrity error'
    status_code = 409


class UserAuditNotFoundError(AuditRouterError):
    title = 'User audit not found error'
    status_code = 404


class TaskAuditNotFoundError(AuditRouterError):
    title = 'Task audit not found error'
    status_code = 404
