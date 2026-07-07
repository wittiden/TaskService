from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded

from app.common.exceptions.base_exception import RouterError
from app.common.exceptions.handlers import app_exception_handler, rate_limit_exceeded_handler

HANDLER_LIST = [
    app_exception_handler,
    rate_limit_exceeded_handler
]

EXCEPTION_LIST = [
    RouterError,
    RateLimitExceeded
]


def setup_handlers(app: FastAPI) -> None:
    for handler, exc_type in zip(HANDLER_LIST, EXCEPTION_LIST):
        app.add_exception_handler(exc_type, handler)
