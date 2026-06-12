from fastapi import APIRouter, Request
from dishka.integrations.fastapi import inject, FromDishka
from sqlalchemy.ext.asyncio import AsyncEngine

from app.infrastructure.http.healthcheck.utils import application_health, database_health

health_router = APIRouter(prefix='/api/v1/health', tags=['health'])


@health_router.get('/app', summary='Application health check')
def app_health_check_endpoint(request: Request) -> dict[str, str]:
    return application_health()


@health_router.get('/db', summary='Database health check')
@inject
async def db_health_check_endpoint(request: Request, async_engine: FromDishka[AsyncEngine]) -> dict[str, str]:
    return await database_health(async_engine)
