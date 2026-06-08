from typing import AsyncGenerator
from dishka import Provider, provide, make_async_container, AsyncContainer, Scope
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, async_sessionmaker, create_async_engine

from app.infrastructure.database.config import DatabaseConfig
from app.modules.users.repository.commands import UserCommandsRepository
from app.modules.users.repository.queries import UserQueriesRepository
from app.modules.users.service.use_cases import CreateUserCase


class DatabaseConfigProvider(Provider):
    """Провайдер по созданию конфигурации бд"""

    @provide(scope=Scope.APP)
    def database_config(self) -> DatabaseConfig:
        return DatabaseConfig()


class DatabaseEngineProvider(Provider):
    """Провайдер по созданию движка бд"""

    @provide(scope=Scope.APP)
    def database_async_engine(self, database_config: DatabaseConfig) -> AsyncEngine:
        return create_async_engine(
            url=database_config.database_url,
            echo=False,
        )


class DatabaseSessionFactoryProvider(Provider):
    """Провайдер по созданию фабрики сессий бд"""

    @provide(scope=Scope.APP)
    def database_async_session_factory(self, async_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            bind=async_engine,
            expire_on_commit=False,
            autoflush=False,
        )


class DatabaseSessionProvider(Provider):
    """Провайдер по созданию сессий бд"""

    @provide(scope=Scope.REQUEST)
    async def database_async_session(self, async_session_factory: async_sessionmaker[AsyncSession]) -> AsyncGenerator[AsyncSession, None]:
        async with async_session_factory() as async_session:
            yield async_session


class CommandsRepositoryProvider(Provider):
    """Провайдер по созданию репозиториев команд"""

    scope = Scope.REQUEST

    @provide
    def user_commands_repo(self, async_session: AsyncSession) -> UserCommandsRepository:
        return UserCommandsRepository(async_session)


class QueriesRepositoryProvider(Provider):
    """Провайдер по созданию репозиториев запросов"""

    scope = Scope.REQUEST

    @provide
    def user_queries_repo(self, async_session: AsyncSession) -> UserQueriesRepository:
        return UserQueriesRepository(async_session)


class UserCasesProvider(Provider):
    """Провайдер по созданию кейсов пользователя"""

    scope = Scope.REQUEST

    @provide
    def create_user_case(self, user_commands: UserCommandsRepository) -> CreateUserCase:
        return CreateUserCase(user_commands)


def create_async_container() -> AsyncContainer:
    return make_async_container(
        DatabaseConfigProvider(),
        DatabaseEngineProvider(),
        DatabaseSessionFactoryProvider(),
        DatabaseSessionProvider(),
        CommandsRepositoryProvider(),
        QueriesRepositoryProvider(),
        UserCasesProvider(),
    )

async_container = create_async_container()
