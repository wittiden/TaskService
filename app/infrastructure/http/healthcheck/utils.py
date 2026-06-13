from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import select

from app.infrastructure.http.healthcheck.exceptions import AppHealthError, DbHealthError, RedisHealthError


def application_health() -> dict[str, str]:
    try:
            return {
            'Status': 'healthy',
            'Service': 'application'
        }
    except Exception as ex:
        raise AppHealthError('Status: unhealthy') from ex


async def database_health(async_engine: AsyncEngine) -> dict[str, str]:
    try:
        async with async_engine.connect() as conn:
            await conn.execute(select(1))

        return {
            'Status': 'healthy',
            'Service': 'database'
        }
    except Exception as ex:
        raise DbHealthError('Status: unhealthy') from ex


async def redis_health(redis_client: Redis) -> dict[str, str]:
    try:
        await redis_client.ping()

        return {
            'Status': 'healthy',
            'Service': 'redis'
        }
    except Exception as ex:
        raise RedisHealthError('Status: unhealthy') from ex
