import pytest
from unittest.mock import AsyncMock

from app.infrastructure.redis.repositories.current_user import RedisCurrentUserRepository
from app.modules.auth.service.use_cases import AuthUserCase
from app.modules.users.repository.commands import UserCommandsRepository
from app.modules.users.repository.queries import UserQueriesRepository
from app.modules.users.service.guard_config import UserGuardConfig
from app.modules.users.service.use_cases import CreateUserCase, UpdateUserCase, DeleteUserCase


@pytest.fixture
def user_commands() -> AsyncMock:
    return AsyncMock(spec=UserCommandsRepository)


@pytest.fixture
def user_queries() -> AsyncMock:
    return AsyncMock(spec=UserQueriesRepository)


@pytest.fixture
def redis_current_user() -> AsyncMock:
    return AsyncMock(spec=RedisCurrentUserRepository)


@pytest.fixture(scope='session')
def user_guard_config() -> UserGuardConfig:
    return UserGuardConfig()

@pytest.fixture
def auth_user() -> AsyncMock:
    return AsyncMock(spec=AuthUserCase)


@pytest.fixture
def create_user_case(user_commands):
    return CreateUserCase(user_commands)


@pytest.fixture
def update_user_case(user_commands, user_queries, redis_current_user):
    return UpdateUserCase(user_commands, user_queries, redis_current_user)


@pytest.fixture
def delete_user_case(user_commands, user_queries, user_guard_config, redis_current_user, auth_user):
    return DeleteUserCase(user_commands, user_queries, user_guard_config, auth_user, redis_current_user)
