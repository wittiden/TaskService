from fastapi import FastAPI

from app.infrastructure.http.middleware.logger import MiddlewareLogger

MIDDLEWARES_CLASS_LIST = [
    MiddlewareLogger
]


def setup_middlewares(app: FastAPI) -> None:
    for middleware in MIDDLEWARES_CLASS_LIST:
        app.add_middleware(middleware)
