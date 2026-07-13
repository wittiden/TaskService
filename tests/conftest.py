from unittest.mock import AsyncMock, Mock

import pytest

from app.infrastructure.redis.repositories.current_user.commands import CurrentUserRedisCommandsRepository
from app.modules.audits.repository.commands import UserAuditCommandsRepository
from app.modules.audits.repository.queries import UserAuditQueriesRepository
from app.modules.audits.service.use_cases import CreateUserAuditCase, ShowUserAuditCase
from app.modules.auth.jwt_config import TokenConfig
from app.modules.auth.repository.commands import AuthCommandsRepository
from app.modules.auth.repository.queries import AuthQueriesRepository
from app.modules.auth.service.use_cases import LoginUserCase, LogoutUserCase, ManageTokenCase, RefreshUserCase, ShowCurrentUserCase
from app.modules.sessions.repository.commands import SessionCommandsRepository
from app.modules.sessions.repository.queries import SessionQueriesRepository
from app.modules.sessions.service.use_cases import DeleteRefreshTokenCase, ShowRefreshTokenCase
from app.modules.users.repository.commands import UserCommandsRepository
from app.modules.users.repository.queries import UserQueriesRepository
from app.modules.users.service.use_cases import CreateUserCase, DeleteUserCase, ManageUserCase, ShowUserCase, UpdateUserCase


@pytest.fixture()
def mock_user_commands() -> AsyncMock:
    return AsyncMock(spec=UserCommandsRepository)


@pytest.fixture()
def mock_user_queries() -> AsyncMock:
    return AsyncMock(spec=UserQueriesRepository)


@pytest.fixture()
def mock_auth_commands() -> AsyncMock:
    return AsyncMock(spec=AuthCommandsRepository)


@pytest.fixture()
def mock_auth_queries() -> AsyncMock:
    return AsyncMock(spec=AuthQueriesRepository)


@pytest.fixture()
def mock_user_audit_commands() -> AsyncMock:
    return AsyncMock(spec=UserAuditCommandsRepository)


@pytest.fixture()
def mock_user_audit_queries() -> AsyncMock:
    return AsyncMock(spec=UserAuditQueriesRepository)


@pytest.fixture()
def mock_session_commands() -> AsyncMock:
    return AsyncMock(spec=SessionCommandsRepository)


@pytest.fixture()
def mock_session_queries() -> AsyncMock:
    return AsyncMock(spec=SessionQueriesRepository)


@pytest.fixture()
def mock_current_user_redis_commands() -> AsyncMock:
    return AsyncMock(spec=CurrentUserRedisCommandsRepository)


@pytest.fixture()
def mock_token_config() -> Mock:
    return Mock(spec=TokenConfig)


@pytest.fixture()
def create_user_audit_mock_case(mock_user_audit_commands) -> CreateUserAuditCase:
    return CreateUserAuditCase(mock_user_audit_commands)


@pytest.fixture()
def mock_create_user_audit_case() -> AsyncMock:
    return AsyncMock(spec=CreateUserAuditCase)


@pytest.fixture()
def show_user_audit_mock_case(mock_user_audit_queries) -> ShowUserAuditCase:
    return ShowUserAuditCase(mock_user_audit_queries)


@pytest.fixture()
def show_refresh_token_mock_case(mock_session_queries) -> ShowRefreshTokenCase:
    return ShowRefreshTokenCase(mock_session_queries)


@pytest.fixture()
def delete_refresh_token_mock_case(mock_session_commands) -> DeleteRefreshTokenCase:
    return DeleteRefreshTokenCase(mock_session_commands)


@pytest.fixture()
def manage_token_mock_case(mock_token_config, mock_auth_commands) -> ManageTokenCase:
    return ManageTokenCase(mock_token_config, mock_auth_commands)


@pytest.fixture()
def login_user_mock_case(manage_token_mock_case, mock_auth_queries) -> LoginUserCase:
    return LoginUserCase(manage_token_mock_case, mock_auth_queries)


@pytest.fixture()
def logout_user_mock_case(mock_auth_commands, mock_token_config, mock_current_user_redis_commands) -> LogoutUserCase:
    return LogoutUserCase(mock_auth_commands, mock_token_config, mock_current_user_redis_commands)


@pytest.fixture()
def mock_logout_user_case() -> AsyncMock:
    return AsyncMock(spec=LogoutUserCase)


@pytest.fixture()
def refresh_user_mock_case(manage_token_mock_case, mock_auth_queries, mock_current_user_redis_commands, mock_token_config, mock_auth_commands) -> RefreshUserCase:
    return RefreshUserCase(manage_token_mock_case, mock_auth_queries, mock_current_user_redis_commands, mock_token_config, mock_auth_commands)


@pytest.fixture()
def show_current_user_mock_case(manage_token_mock_case, mock_auth_queries, mock_current_user_redis_commands) -> ShowCurrentUserCase:
    return ShowCurrentUserCase(manage_token_mock_case, mock_auth_queries, mock_current_user_redis_commands)


@pytest.fixture()
def create_user_mock_case(mock_user_commands) -> CreateUserCase:
    return CreateUserCase(mock_user_commands)


@pytest.fixture()
def update_user_mock_case(mock_user_commands, mock_current_user_redis_commands, mock_create_user_audit_case) -> UpdateUserCase:
    return UpdateUserCase(mock_user_commands, mock_current_user_redis_commands, mock_create_user_audit_case)


@pytest.fixture()
def delete_user_mock_case(mock_user_commands, mock_logout_user_case, mock_create_user_audit_case) -> DeleteUserCase:
    return DeleteUserCase(mock_user_commands, mock_logout_user_case, mock_create_user_audit_case)


@pytest.fixture()
def manage_user_mock_case(mock_user_commands, mock_logout_user_case, mock_user_queries, mock_create_user_audit_case) -> ManageUserCase:
    return ManageUserCase(mock_user_commands, mock_logout_user_case, mock_user_queries, mock_create_user_audit_case)


@pytest.fixture()
def show_user_mock_case(mock_user_queries) -> ShowUserCase:
    return ShowUserCase(mock_user_queries)
