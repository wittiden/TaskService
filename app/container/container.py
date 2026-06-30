from typing import AsyncGenerator

from dishka import Provider, provide, Scope, AsyncContainer, make_async_container
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession, async_sessionmaker

from app.infrastructure.database.config import DatabaseConfig


class DatabaseConfigProvider(Provider):
    """Провайдер по созданию конфигурации бд"""

    @provide(scope=Scope.APP)
    def database_config(self) -> DatabaseConfig:
        return DatabaseConfig()


class DatabaseEngineProvider(Provider):
    """Провайдер по созданию движка бд"""

    @provide(scope=Scope.APP)
    async def database_engine(self, database_config: DatabaseConfig) -> AsyncGenerator[AsyncEngine, None]:
        async_engine = create_async_engine(
            url=database_config.database_url,
            echo=False,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            pool_timeout=5,
            connect_args={
                'command_timeout': 5
            }
        )

        yield async_engine

        await async_engine.dispose()


class AsyncSessionmakerProvider(Provider):
    """Провайдер по созданию фабрики сессий в бд"""

    @provide(scope=Scope.APP)
    def create_async_sessionmaker(self, async_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            bind=async_engine,
            autoflush=False,
            expire_on_commit=False,
        )


class AsyncSessionProvider(Provider):
    """Провайдер по созданию сессий в бд"""

    @provide(scope=Scope.REQUEST)
    async def create_async_session(self, async_session_factory: async_sessionmaker[AsyncSession]) -> AsyncGenerator[AsyncSession, None]:
        async with async_session_factory() as async_session:
            yield async_session


def create_async_container() -> AsyncContainer:
    return make_async_container(
        DatabaseConfigProvider(),
        DatabaseEngineProvider(),
        AsyncSessionmakerProvider(),
        AsyncSessionProvider(),
    )

async_container = create_async_container()
