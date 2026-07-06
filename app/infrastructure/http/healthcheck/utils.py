from redis.asyncio import Redis, RedisError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine

from app.infrastructure.http.healthcheck.exceptions import ApplicationHealthError, DatabaseHealthError, RedisHealthError


def application_healthcheck() -> dict:
    try:
        return {
            'service': 'application',
            'status': 'healthy'
        }

    except Exception as ex:
        raise ApplicationHealthError('status unhealthy') from ex


async def database_healthcheck(async_engine: AsyncEngine) -> dict:
    try:
        async with async_engine.connect() as engine:
            await engine.execute(select(1))

            return {
                'service': 'database',
                'status': 'healthy'
            }

    except Exception as exc:
        raise DatabaseHealthError(str(exc))


async def redis_healthcheck(redis_client: Redis) -> dict:
    try:
        await redis_client.ping()

        return {
            "service": "redis",
            "status": "healthy"
        }

    except RedisError as exc:
        raise RedisHealthError(str(exc))
