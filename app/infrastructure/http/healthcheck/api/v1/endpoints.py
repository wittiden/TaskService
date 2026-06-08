from fastapi import APIRouter, Request
from dishka.integrations.fastapi import inject, FromDishka
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import select

health_router = APIRouter(prefix='/api/v1/health', tags=['health'])


@health_router.get('/app', summary='Application health check')
def app_health_check_endpoint(request: Request) -> dict[str, str]:
    return {
        'Application': 'healthy'
    }


@health_router.get('/db', summary='Database health check')
@inject
async def db_health_check_endpoint(request: Request, async_engine: FromDishka[AsyncEngine]) -> dict[str, str]:
    async with async_engine.connect() as conn:
        await conn.execute(select(1))

        return {
            'Database': 'healthy'
        }
