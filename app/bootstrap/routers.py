from fastapi import FastAPI

from app.infrastructure.http.healthcheck.api.v1.endpoints import health_router
from app.modules.audits.api.v1.endpoints import admin_user_audits_router
from app.modules.auth.api.v1.endpoints import auth_router
from app.modules.sessions.api.v1.endpoints import admin_tokens_router
from app.modules.users.api.v1.endpoints import users_router, admin_users_router

ROUTER_LIST = [
    health_router,
    auth_router,
    users_router,
    admin_users_router,
    admin_user_audits_router,
    admin_tokens_router,
]


def setup_routers(app: FastAPI) -> None:
    for router in ROUTER_LIST:
        app.include_router(router)
