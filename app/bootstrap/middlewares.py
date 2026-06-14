from fastapi import FastAPI
from slowapi.middleware import SlowAPIMiddleware

from app.infrastructure.http.middleware.logger import MiddlewareLogger
from app.infrastructure.http.middleware.timeout import TimeoutMiddleware


def setup_middlewares(app: FastAPI) -> None:
    app.add_middleware(MiddlewareLogger)
    app.add_middleware(TimeoutMiddleware, timeout=15)
    app.add_middleware(SlowAPIMiddleware)
