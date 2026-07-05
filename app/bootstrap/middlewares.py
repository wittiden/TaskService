from fastapi import FastAPI

from app.infrastructure.http.middleware.logger import LoggerMiddleware
from app.infrastructure.http.middleware.timeout import TimeoutMiddleware

MIDDLEWARE_LIST = [
    TimeoutMiddleware,
    LoggerMiddleware,
]

def setup_middlewares(app: FastAPI):
    for middleware in MIDDLEWARE_LIST:
        app.add_middleware(middleware)
