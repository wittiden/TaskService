from app.common.exceptions.base_ex import RouterError


class AuthRouterError(RouterError):
    status_code = 400
    title = 'Auth router error'


class InvalidTokenVersionError(AuthRouterError):
    status_code = 409
    title = 'Invalid token version error'


class ForbiddenError(AuthRouterError):
    status_code = 403
    title = 'Forbidden error'


class RevokedTokenError(AuthRouterError):
    status_code = 409
    title = 'Revoked token error'


class TokenInvalidError(AuthRouterError):
    status_code = 400
    title = 'Token invalid error'


class ExpiredTokenError(AuthRouterError):
    status_code = 409
    title = 'Expired token error'


class InvalidTokenTypeError(AuthRouterError):
    status_code = 400
    title = 'Invalid token type error'


class InvalidTokenAudienceError(AuthRouterError):
    status_code = 409
    title = 'Invalid token audience error'


class TokenNotFoundError(AuthRouterError):
    status_code = 404
    title = 'Token not found error'


class TokenRetentionPeriodError(AuthRouterError):
    status_code = 409
    title = 'Token retention period error'
