from typing import AsyncGenerator

from redis.asyncio import Redis
from dishka import Provider, provide, Scope, AsyncContainer, make_async_container
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession, async_sessionmaker

from app.infrastructure.redis.config import RedisConfig
from app.infrastructure.redis.repositories.current_user.commands import CurrentUserRedisCommandsRepository
from app.infrastructure.unit_of_work.uow import UnitOfWork
from app.modules.auth.jwt_config import TokenConfig
from app.infrastructure.database.config import DatabaseConfig
from app.modules.auth.repository.commands import AuthCommandsRepository
from app.modules.auth.repository.queries import AuthQueriesRepository
from app.modules.auth.service.use_cases import ManageTokenCase, LoginUserCase, ShowCurrentUserCase, LogoutUserCase, \
    RefreshUserCase
from app.modules.sessions.repository.commands import SessionCommandsRepository
from app.modules.sessions.repository.queries import SessionQueriesRepository
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


class RedisConfigProvider(Provider):
    """Провайдер по созданию конфигурации Redis"""

    @provide(scope=Scope.APP)
    def redis_config(self) -> RedisConfig:
        return RedisConfig()


class RedisClientProvider(Provider):
    """Провайдер по созданию клиента Redis"""

    @provide(scope=Scope.APP)
    async def redis_client(self, redis_config: RedisConfig) -> AsyncGenerator[Redis, None]:
        redis = Redis(
            host=redis_config.REDIS_HOST,
            port=redis_config.REDIS_PORT,
            password=redis_config.REDIS_PASS,
            db=redis_config.REDIS_DB,
            decode_responses=True,
            socket_timeout=3,
            socket_connect_timeout=1,
        )

        try:
            yield redis
        finally:
            await redis.aclose()


class TokenConfigProvider(Provider):
    """Провайдер по созданию конфигурации токенов"""

    @provide(scope=Scope.APP)
    def token_config(self) -> TokenConfig:
        return TokenConfig()


class RedisRepositoriesProvider(Provider):
    """Провайдер по созданию репозиториев Redis"""

    scope = Scope.APP

    @provide
    def current_user_redis_commands(self, redis_client: Redis) -> CurrentUserRedisCommandsRepository:
        return CurrentUserRedisCommandsRepository(redis_client)


class UnitOfWorkProvider(Provider):
    """Провайдер по созданию реализации паттерна uow"""

    @provide(scope=Scope.REQUEST)
    async def unit_of_work(self, async_session: AsyncSession) -> AsyncGenerator[UnitOfWork, None]:
        async with UnitOfWork(async_session) as uow:
            yield uow


class CommandsRepositoryProvider(Provider):
    """Провайдер по созданию commands репозиториев"""

    scope = Scope.REQUEST

    @provide
    def user_commands_repo(self, async_session: AsyncSession) -> UserCommandsRepository:
        return UserCommandsRepository(async_session)

    @provide
    def auth_commands_repo(self, async_session: AsyncSession) -> AuthCommandsRepository:
        return AuthCommandsRepository(async_session)

    @provide
    def session_commands_repo(self, async_session: AsyncSession) -> SessionCommandsRepository:
        return SessionCommandsRepository(async_session)


class QueriesRepositoryProvider(Provider):
    """Провайдер по созданию queries репозиториев"""

    scope = Scope.REQUEST

    @provide
    def user_queries_repo(self, async_session: AsyncSession) -> UserQueriesRepository:
        return UserQueriesRepository(async_session)

    @provide
    def auth_queries_repo(self, async_session: AsyncSession) -> AuthQueriesRepository:
        return AuthQueriesRepository(async_session)

    @provide
    def session_queries_repo(self, async_session: AsyncSession) -> SessionQueriesRepository:
        return SessionQueriesRepository(async_session)


class UserUseCasesProvider(Provider):
    """Провайдер по созданию кейсов пользователя"""

    scope = Scope.REQUEST

    @provide
    def create_user_case(self, user_commands: UserCommandsRepository) -> CreateUserCase:
        return CreateUserCase(user_commands)


class AuthUseCasesProvider(Provider):
    """Провайдер по созданию аутентификационных кейсов"""

    scope = Scope.REQUEST

    @provide
    def manage_token_case(self, token_config: TokenConfig, auth_commands: AuthCommandsRepository) -> ManageTokenCase:
        return ManageTokenCase(token_config, auth_commands)

    @provide
    def login_user_case(self, auth_queries: AuthQueriesRepository, manage_token_case: ManageTokenCase) -> LoginUserCase:
        return LoginUserCase(manage_token_case, auth_queries)

    @provide
    def logout_user_case(self, auth_commands: AuthCommandsRepository, token_config: TokenConfig, current_user_redis_commands: CurrentUserRedisCommandsRepository) -> LogoutUserCase:
        return LogoutUserCase(auth_commands, token_config, current_user_redis_commands)

    @provide
    def refresh_user_case(self, auth_queries: AuthQueriesRepository, auth_commands: AuthCommandsRepository, manage_token_case: ManageTokenCase, token_config: TokenConfig, current_user_redis_commands: CurrentUserRedisCommandsRepository) -> RefreshUserCase:
        return RefreshUserCase(manage_token_case, auth_queries, current_user_redis_commands, token_config, auth_commands)

    @provide
    def show_current_user_case(self, manage_token_case: ManageTokenCase, auth_queries: AuthQueriesRepository, current_user_redis_commands: CurrentUserRedisCommandsRepository) -> ShowCurrentUserCase:
        return ShowCurrentUserCase(manage_token_case, auth_queries, current_user_redis_commands)


def create_async_container() -> AsyncContainer:
    return make_async_container(
        DatabaseConfigProvider(),
        DatabaseEngineProvider(),
        AsyncSessionmakerProvider(),
        AsyncSessionProvider(),
        RedisConfigProvider(),
        RedisClientProvider(),
        TokenConfigProvider(),
        UnitOfWorkProvider(),
        RedisRepositoriesProvider(),
        CommandsRepositoryProvider(),
        QueriesRepositoryProvider(),
        UserUseCasesProvider(),
        AuthUseCasesProvider(),
    )

async_container = create_async_container()
