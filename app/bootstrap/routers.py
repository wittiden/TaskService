from fastapi import FastAPI

from app.infrastructure.http.healthcheck.api.v1.endpoints import health_router
from app.modules.auth.api.v1.endpoints import admin_refresh_tokens_router, auth_router

ROUTERS_LIST = [
    health_router,
    auth_router,
    admin_refresh_tokens_router
]


def setup_routers(app: FastAPI) -> None:
    for router in ROUTERS_LIST:
        app.include_router(router)
