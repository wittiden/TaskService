from unittest.mock import AsyncMock, Mock

import pytest

from app.infrastructure.redis.repositories.current_user.commands import (
    CurrentUserRedisCommandsRepository,
)
from app.modules.audits.repository.commands import (
    TaskAuditCommandsRepository,
    UserAuditCommandsRepository,
)
from app.modules.audits.repository.queries import UserAuditQueriesRepository
from app.modules.audits.service.use_cases import CreateTaskAuditCase, CreateUserAuditCase
from app.modules.auth.jwt_config import TokenConfig
from app.modules.auth.repository.commands import AuthCommandsRepository
from app.modules.auth.repository.queries import AuthQueriesRepository
from app.modules.auth.service.use_cases import (
    LoginUserCase,
    LogoutUserCase,
    ManageTokenCase,
    RefreshUserCase,
    ShowCurrentUserCase,
)
from app.modules.sessions.repository.commands import SessionCommandsRepository
from app.modules.sessions.repository.queries import SessionQueriesRepository
from app.modules.sessions.service.use_cases import (
    DeleteRefreshTokenCase,
)
from app.modules.tasks.config import TaskConfig
from app.modules.tasks.repository.commands import TaskCommandsRepository
from app.modules.tasks.repository.queries import TaskQueriesRepository
from app.modules.tasks.service.use_cases import (
    CreateTaskCase,
    DeleteTaskCase,
    ManageTaskCase,
    UpdateTaskCase,
)
from app.modules.users.repository.commands import UserCommandsRepository
from app.modules.users.repository.queries import UserQueriesRepository
from app.modules.users.service.use_cases import (
    CreateUserCase,
    DeleteUserCase,
    ManageUserCase,
    UpdateUserCase,
)


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
def delete_refresh_token_mock_case(mock_session_commands) -> DeleteRefreshTokenCase:
    return DeleteRefreshTokenCase(mock_session_commands)


@pytest.fixture()
def manage_token_mock_case(mock_token_config, mock_auth_commands) -> ManageTokenCase:
    return ManageTokenCase(mock_token_config, mock_auth_commands)


@pytest.fixture()
def mock_manage_token_case() -> AsyncMock:
    return AsyncMock(spec=ManageTokenCase)


@pytest.fixture()
def login_user_mock_case(mock_manage_token_case, mock_auth_queries) -> LoginUserCase:
    return LoginUserCase(mock_manage_token_case, mock_auth_queries)


@pytest.fixture()
def logout_user_mock_case(
    mock_auth_commands, mock_token_config, mock_current_user_redis_commands
) -> LogoutUserCase:
    return LogoutUserCase(mock_auth_commands, mock_token_config, mock_current_user_redis_commands)


@pytest.fixture()
def mock_logout_user_case() -> AsyncMock:
    return AsyncMock(spec=LogoutUserCase)


@pytest.fixture()
def refresh_user_mock_case(
    mock_manage_token_case,
    mock_auth_queries,
    mock_current_user_redis_commands,
    mock_token_config,
    mock_auth_commands,
) -> RefreshUserCase:
    return RefreshUserCase(
        mock_manage_token_case,
        mock_auth_queries,
        mock_current_user_redis_commands,
        mock_token_config,
        mock_auth_commands,
    )


@pytest.fixture()
def show_current_user_mock_case(
    mock_manage_token_case, mock_auth_queries, mock_current_user_redis_commands
) -> ShowCurrentUserCase:
    return ShowCurrentUserCase(
        mock_manage_token_case, mock_auth_queries, mock_current_user_redis_commands
    )


@pytest.fixture()
def create_user_mock_case(mock_user_commands) -> CreateUserCase:
    return CreateUserCase(mock_user_commands)


@pytest.fixture()
def update_user_mock_case(
    mock_user_commands, mock_current_user_redis_commands, mock_create_user_audit_case
) -> UpdateUserCase:
    return UpdateUserCase(
        mock_user_commands,
        mock_current_user_redis_commands,
        mock_create_user_audit_case,
    )


@pytest.fixture()
def delete_user_mock_case(
    mock_user_commands, mock_logout_user_case, mock_create_user_audit_case
) -> DeleteUserCase:
    return DeleteUserCase(mock_user_commands, mock_logout_user_case, mock_create_user_audit_case)


@pytest.fixture()
def manage_user_mock_case(
    mock_user_commands,
    mock_logout_user_case,
    mock_user_queries,
    mock_create_user_audit_case,
) -> ManageUserCase:
    return ManageUserCase(
        mock_user_commands,
        mock_logout_user_case,
        mock_user_queries,
        mock_create_user_audit_case,
    )


@pytest.fixture()
def mock_task_commands_repo() -> AsyncMock:
    return AsyncMock(spec=TaskCommandsRepository)


@pytest.fixture()
def mock_task_queries_repo() -> AsyncMock:
    return AsyncMock(spec=TaskQueriesRepository)


@pytest.fixture()
def mock_task_config() -> Mock:
    return Mock(spec=TaskConfig)


@pytest.fixture()
def create_task_mock_case(mock_task_commands_repo, mock_task_config, mock_task_queries_repo):
    return CreateTaskCase(mock_task_commands_repo, mock_task_config, mock_task_queries_repo)


@pytest.fixture()
def mock_create_tack_audit_case() -> AsyncMock:
    return AsyncMock(spec=CreateTaskAuditCase)


@pytest.fixture()
def update_task_mock_case(
    mock_task_queries_repo, mock_task_commands_repo, mock_create_tack_audit_case
) -> UpdateTaskCase:
    return UpdateTaskCase(
        mock_task_commands_repo, mock_task_queries_repo, mock_create_tack_audit_case
    )


@pytest.fixture()
def manage_task_mock_case(mock_task_commands_repo, mock_create_tack_audit_case) -> ManageTaskCase:
    return ManageTaskCase(mock_task_commands_repo, mock_create_tack_audit_case)


@pytest.fixture()
def delete_task_mock_case(mock_task_commands_repo) -> DeleteTaskCase:
    return DeleteTaskCase(mock_task_commands_repo)


@pytest.fixture()
def mock_task_audit_commands_repo() -> AsyncMock:
    return AsyncMock(spec=TaskAuditCommandsRepository)


@pytest.fixture()
def create_task_audit_mock_case(mock_task_audit_commands_repo) -> CreateTaskAuditCase:
    return CreateTaskAuditCase(mock_task_audit_commands_repo)
