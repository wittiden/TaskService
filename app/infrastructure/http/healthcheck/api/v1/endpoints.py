from fastapi import APIRouter
from dishka.integrations.fastapi import FromDishka, inject
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine

from app.infrastructure.http.healthcheck.utils import application_healthcheck, database_healthcheck, redis_healthcheck

health_router = APIRouter(prefix='/api/v1/health', tags=['health'])


@health_router.get('/app', response_model=dict, summary='Application healthcheck')
def application_healthcheck_endpoint() -> dict:
    return application_healthcheck()


@health_router.get('/db', response_model=dict, summary='Database healthcheck')
@inject
async def database_healthcheck_endpoint(async_engine: FromDishka[AsyncEngine]) -> dict:
    return await database_healthcheck(async_engine)


@health_router.get('/redis', response_model=dict, summary='Redis healthcheck')
@inject
async def redis_healthcheck_endpoint(redis_client: FromDishka[Redis]) -> dict:
    return await redis_healthcheck(redis_client)
