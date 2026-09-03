from celery_farm import create_beat_app, create_task_app
from fastapi import FastAPI

from app.common.task_service.utils import celery
from app.infrastructure.http.healthcheck.api.v1.endpoints import health_router
from app.modules.audits.api.v1.routers.read import (
    read_admin_task_audits_router,
    read_admin_user_audits_router,
)
from app.modules.auth.api.v1.routers.manage import auth_router
from app.modules.sessions.api.v1.routers.delete import delete_admin_sessions_router
from app.modules.sessions.api.v1.routers.read import read_admin_sessions_router
from app.modules.tasks.api.v1.routers.create import create_tasks_router
from app.modules.tasks.api.v1.routers.delete import delete_tasks_router
from app.modules.tasks.api.v1.routers.read import read_tasks_router
from app.modules.tasks.api.v1.routers.update import update_tasks_router
from app.modules.users.api.v1.routers.create import create_users_router
from app.modules.users.api.v1.routers.delete import delete_admin_users_router
from app.modules.users.api.v1.routers.read import read_admin_users_router, read_users_router
from app.modules.users.api.v1.routers.update import update_admin_users_router, update_users_router

ROUTER_LIST = [
    health_router,
    auth_router,
    create_users_router,
    update_users_router,
    update_admin_users_router,
    delete_admin_users_router,
    read_users_router,
    read_admin_users_router,
    read_admin_user_audits_router,
    create_tasks_router,
    update_tasks_router,
    delete_tasks_router,
    read_tasks_router,
    read_admin_task_audits_router,
    delete_admin_sessions_router,
    read_admin_sessions_router,
]

if celery:
    celery_task_app = create_task_app(celery)
    celery_beat_app = create_beat_app(celery)

    ROUTER_LIST.insert(1, celery_task_app.router)
    ROUTER_LIST.insert(2, celery_beat_app.router)


def setup_routers(app: FastAPI) -> None:
    for router in ROUTER_LIST:
        app.include_router(router)
