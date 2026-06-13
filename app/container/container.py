from typing import AsyncGenerator
from redis.asyncio import Redis
from dishka import Provider, provide, make_async_container, AsyncContainer, Scope
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, async_sessionmaker, create_async_engine

from app.common.security.jwt_config import JWTConfig
from app.infrastructure.database.config import DatabaseConfig
from app.infrastructure.redis.config import RedisConfig
from app.infrastructure.unit_of_work.uow import ProgramUnitOfWork
from app.modules.auth.repository.commands import RefreshTokenCommandsRepository
from app.modules.auth.repository.queries import RefreshTokenQueriesRepository
from app.modules.auth.service.use_cases import ManageTokenCase, AuthUserCase, CurrentUserCase, ShowRefreshTokenCase, \
    DeleteRefreshTokenCase
from app.modules.users.repository.commands import UserCommandsRepository
from app.modules.users.repository.queries import UserQueriesRepository
from app.modules.users.service.guard_config import UserGuardConfig
from app.modules.users.service.use_cases import CreateUserCase, UpdateUserCase, DeleteUserCase, ShowUserCase, \
    ManageUserCase


class DatabaseConfigProvider(Provider):
    """Провайдер по созданию конфигурации бд"""

    @provide(scope=Scope.APP)
    def database_config(self) -> DatabaseConfig:
        return DatabaseConfig()


class DatabaseEngineProvider(Provider):
    """Провайдер по созданию движка бд"""

    @provide(scope=Scope.APP)
    async def database_async_engine(self, database_config: DatabaseConfig) -> AsyncGenerator[AsyncEngine, None]:
        async_engine = create_async_engine(
            url=database_config.database_url,
            echo=False,
        )

        try:
            yield async_engine
        finally:
            await async_engine.dispose()


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


class ProgramUnitOfWorkProvider(Provider):
    """Провайдер по созданию контекстного менеджера uow"""

    @provide(scope=Scope.REQUEST)
    async def program_uow(self, async_session: AsyncSession) -> AsyncGenerator[ProgramUnitOfWork, None]:
        async with ProgramUnitOfWork(async_session) as uow:
            yield uow


class RedisConfigProvider(Provider):
    """Провайдер для создания конфигурации redis"""

    @provide(scope=Scope.APP)
    def redis_config(self) -> RedisConfig:
        return RedisConfig()


class RedisClientProvider(Provider):
    """Провайдер для создания клиента redis"""

    @provide(scope=Scope.APP)
    async def redis_client(self, redis_config: RedisConfig) -> AsyncGenerator[Redis, None]:
        redis = Redis(
            host=redis_config.REDIS_HOST,
            port=redis_config.REDIS_PORT,
            password=redis_config.REDIS_PASS,
            decode_responses=True,
            db=redis_config.REDIS_DB,
        )

        try:
            yield redis
        finally:
            await redis.aclose()


class JWTConfigProvider(Provider):
    """Провайдер для конфигурации jwt токенов"""

    @provide(scope=Scope.APP)
    def jwt_config(self) -> JWTConfig:
        return JWTConfig()


class CommandsRepositoryProvider(Provider):
    """Провайдер по созданию репозиториев команд"""

    scope = Scope.REQUEST

    @provide
    def user_commands_repo(self, async_session: AsyncSession) -> UserCommandsRepository:
        return UserCommandsRepository(async_session)

    @provide
    def auth_commands_repo(self, async_session: AsyncSession) -> RefreshTokenCommandsRepository:
        return RefreshTokenCommandsRepository(async_session)


class QueriesRepositoryProvider(Provider):
    """Провайдер по созданию репозиториев запросов"""

    scope = Scope.REQUEST

    @provide
    def user_queries_repo(self, async_session: AsyncSession) -> UserQueriesRepository:
        return UserQueriesRepository(async_session)

    @provide
    def auth_queries_repo(self, async_session: AsyncSession) -> RefreshTokenQueriesRepository:
        return RefreshTokenQueriesRepository(async_session)


class AuthCasesProvider(Provider):
    """Провайдер по созданию кейсов аутентификации"""

    scope = Scope.REQUEST

    @provide
    def manage_token_case(self, jwt_config: JWTConfig, refresh_token_commands: RefreshTokenCommandsRepository) -> ManageTokenCase:
        return ManageTokenCase(jwt_config, refresh_token_commands)

    @provide
    def auth_user_case(self, user_queries: UserQueriesRepository, manage_token_case: ManageTokenCase, refresh_token_commands: RefreshTokenCommandsRepository, refresh_token_queries: RefreshTokenQueriesRepository, jwt_config: JWTConfig) -> AuthUserCase:
        return AuthUserCase(user_queries, manage_token_case, refresh_token_commands, refresh_token_queries, jwt_config)

    @provide
    def current_user_case(self, user_queries: UserQueriesRepository, manage_token_case: ManageTokenCase) -> CurrentUserCase:
        return CurrentUserCase(user_queries, manage_token_case)

    @provide
    def show_refresh_token_case(self, refresh_token_queries: RefreshTokenQueriesRepository) -> ShowRefreshTokenCase:
        return ShowRefreshTokenCase(refresh_token_queries)

    @provide
    def delete_refresh_token_case(self, refresh_token_queries: RefreshTokenQueriesRepository, refresh_token_commands: RefreshTokenCommandsRepository, jwt_config: JWTConfig) -> DeleteRefreshTokenCase:
        return DeleteRefreshTokenCase(refresh_token_queries, refresh_token_commands, jwt_config)


class UserGuardConfigProvider(Provider):
    """Провайдер по созданию конфигурации бизнес правил пользователей"""

    @provide(scope=Scope.APP)
    def user_guard_config(self) -> UserGuardConfig:
        return UserGuardConfig()


class UserCasesProvider(Provider):
    """Провайдер по созданию кейсов пользователя"""

    scope = Scope.REQUEST

    @provide
    def create_user_case(self, user_commands: UserCommandsRepository) -> CreateUserCase:
        return CreateUserCase(user_commands)

    @provide
    def update_user_case(self, user_commands: UserCommandsRepository, user_queries: UserQueriesRepository) -> UpdateUserCase:
        return UpdateUserCase(user_commands, user_queries)

    @provide
    def delete_user_case(self, user_commands: UserCommandsRepository, user_queries: UserQueriesRepository, user_guard_config: UserGuardConfig, auth_user_case: AuthUserCase) -> DeleteUserCase:
        return DeleteUserCase(user_commands, user_queries, user_guard_config, auth_user_case)

    @provide
    def show_user_case(self, user_queries: UserQueriesRepository) -> ShowUserCase:
        return ShowUserCase(user_queries)

    @provide
    def manage_user_case(self, user_commands: UserCommandsRepository, user_queries: UserQueriesRepository, auth_user_case: AuthUserCase) -> ManageUserCase:
        return ManageUserCase(user_commands, user_queries, auth_user_case)


def create_async_container() -> AsyncContainer:
    return make_async_container(
        DatabaseConfigProvider(),
        DatabaseEngineProvider(),
        DatabaseSessionFactoryProvider(),
        DatabaseSessionProvider(),
        ProgramUnitOfWorkProvider(),
        RedisConfigProvider(),
        RedisClientProvider(),
        JWTConfigProvider(),
        CommandsRepositoryProvider(),
        QueriesRepositoryProvider(),
        AuthCasesProvider(),
        UserGuardConfigProvider(),
        UserCasesProvider(),
    )

async_container = create_async_container()
