from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine

from app.infrastructure.http.healthcheck.exceptions import ApplicationError


def application_healthcheck() -> dict:
    try:
        return {
            'service': 'application',
            'status': 'healthy'
        }
    except Exception as ex:
        raise ApplicationError('Unhealthy application') from ex


async def database_healthcheck(async_engine: AsyncEngine) -> dict:
    try:
        async with async_engine.connect() as engine:
            await engine.execute(select(1))

            return {
                'service': 'database',
                'status': 'healthy'
            }

    except Exception as ex:
        raise ApplicationError('Unhealthy application') from ex
