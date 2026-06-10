from app.common.exceptions.base_ex import RouterError


class UserRouterError(RouterError):
    status_code = 400
    title = 'User router error'


class EmailIsExistError(UserRouterError):
    status_code = 409
    title = 'Email is exist error'


class InvalidPassError(UserRouterError):
    status_code = 401
    title = 'Invalid password error'


class UserNotFoundError(UserRouterError):
    status_code = 404
    title = 'User not found error'


class UserDeletionGracePeriodError(UserRouterError):
    status_code = 409
    title = 'User grace period error'


class UserAlreadyBlockedError(UserRouterError):
    status_code = 409
    title = 'User already blocked error'


class UserAlreadyUnBlockedError(UserRouterError):
    status_code = 409
    title = 'User already unblocked error'


class UserAlreadyClosedError(UserRouterError):
    status_code = 409
    title = 'User already blocked error'


class ClosedUserError(UserRouterError):
    status_code = 409
    title = 'Closed user error'


class BlockedUserError(UserRouterError):
    status_code = 409
    title = 'Blocked user error'


class SamePasswordsError(UserRouterError):
    status_code = 409
    title = 'Same passwords error'