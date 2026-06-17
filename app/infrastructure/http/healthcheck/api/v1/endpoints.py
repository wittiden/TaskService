from fastapi import APIRouter
from dishka.integrations.fastapi import inject, FromDishka
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine

from app.infrastructure.http.healthcheck.utils import application_health, database_health, redis_health

health_router = APIRouter(prefix='/api/v1/health', tags=['health'])


@health_router.get('/app', summary='Application healthcheck')
def app_healthcheck_endpoint() -> dict[str, str]:
    return application_health()


@health_router.get('/db', summary='Database healthcheck')
@inject
async def db_healthcheck_endpoint(async_engine: FromDishka[AsyncEngine]) -> dict[str, str]:
    return await database_health(async_engine)


@health_router.get('/redis', summary='Redis healthcheck')
@inject
async def redis_healthcheck_endpoint(redis_client: FromDishka[Redis]) -> dict[str, str]:
    return await redis_health(redis_client)
