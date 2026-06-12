from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import select


def application_health() -> dict[str, str]:
    return {
        'Application': 'healthy'
    }


async def database_health(async_engine: AsyncEngine) -> dict[str, str]:
    async with async_engine.connect() as conn:
        await conn.execute(select(1))
        await conn.close()

        return {
            'Database': 'healthy'
        }
