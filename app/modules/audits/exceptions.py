from app.common.exceptions.base_exception import RouterError


class UserAuditRouterError(RouterError):
    title = 'User audits router error'
    status_code = 400


class UserAuditModelIntegrityError(UserAuditRouterError):
    title = 'User audits model integrity error'
    status_code = 409


class UserAuditNotFoundError(UserAuditRouterError):
    title = 'User audits not found error'
    status_code = 404
