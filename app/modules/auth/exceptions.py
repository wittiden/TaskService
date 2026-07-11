from app.common.exceptions.base_exception import RouterError


class AuthRouterError(RouterError):
    title = 'Auth router error'
    status_code = 400


class PassVerifyError(AuthRouterError):
    title = 'Pass verify error'
    status_code = 401


class InvalidTokenSignatureError(AuthRouterError):
    title = 'Invalid token signature error'
    status_code = 401


class InvalidTokenAudienceError(AuthRouterError):
    title = 'Invalid token audience error'
    status_code = 401


class InvalidTokenAlgorithmError(AuthRouterError):
    title = 'Invalid token algorithm error'
    status_code = 401


class InvalidTokenKeyError(AuthRouterError):
    title = 'Invalid token key error'
    status_code = 401


class DecodeTokenError(AuthRouterError):
    title = 'Decode token error'
    status_code = 401


class TokenInvalidError(AuthRouterError):
    title = 'Token invalid error'
    status_code = 401


class ForbiddenError(AuthRouterError):
    title = 'Forbidden error'
    status_code = 403


class InvalidTokenVersionError(AuthRouterError):
    title = 'Invalid token version error'
    status_code = 409


class RevokedTokenError(AuthRouterError):
    title = 'Revoked token error'
    status_code = 401
