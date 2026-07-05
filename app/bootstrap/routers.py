from fastapi import FastAPI

from app.modules.auth.api.v1.endpoints import auth_router
from app.modules.sessions.api.v1.endpoints import admin_tokens_router
from app.modules.users.api.v1.endpoints import users_router, admin_users_router, vip_users_router

ROUTER_LIST = [
    users_router,
    admin_users_router,
    vip_users_router,
    auth_router,
    admin_tokens_router
]


def setup_routers(app: FastAPI) -> None:
    for router in ROUTER_LIST:
        app.include_router(router)
