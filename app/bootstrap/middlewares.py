from fastapi import FastAPI
from slowapi.middleware import SlowAPIMiddleware

from app.infrastructure.http.middleware.logger import LoggerMiddleware
from app.infrastructure.http.middleware.timeout import TimeoutMiddleware

MIDDLEWARE_LIST = [
    LoggerMiddleware,
    TimeoutMiddleware,
    SlowAPIMiddleware
]

def setup_middlewares(app: FastAPI):
    for middleware in MIDDLEWARE_LIST:
        app.add_middleware(middleware)
