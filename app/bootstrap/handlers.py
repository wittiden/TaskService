from fastapi import FastAPI

from app.common.exceptions.base_exception import RouterError
from app.common.exceptions.handler import app_exception_handler

HANDLER_LIST = [
    app_exception_handler
]

EXCEPTION_LIST = [
    RouterError
]


def setup_handlers(app: FastAPI) -> None:
    for handler, exc_type in zip(HANDLER_LIST, EXCEPTION_LIST):
        app.add_exception_handler(exc_type, handler)
