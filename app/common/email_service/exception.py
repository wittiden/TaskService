from app.common.exceptions.base_exception import RouterError


class EmailRouterError(RouterError):
    title = 'Email router error'
    status_code = 500


class SendEmailError(EmailRouterError):
    title = 'Send email error'
    status_code = 500


class TimeoutEmailError(EmailRouterError):
    title = 'Timeout email error'
    status_code = 504
