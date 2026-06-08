from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from slowapi.extension import _rate_limit_exceeded_handler

from app.common.exceptions.base_ex import RouterError
from app.common.exceptions.handler_ex import app_exception_handler

EX_TYPE_LIST = [
    RouterError,
    RateLimitExceeded
]

HANDLERS_LIST = [
    app_exception_handler,
    _rate_limit_exceeded_handler,
]


def setup_handlers(app: FastAPI) -> None:
    for ex_type, handler in zip(EX_TYPE_LIST, HANDLERS_LIST):
        app.add_exception_handler(ex_type, handler)
