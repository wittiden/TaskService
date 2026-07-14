import pytest
from pytest_mock import MockerFixture

from app.modules.auth.contracts.dtos import TokenInfoDTO
from app.modules.auth.exceptions import ForbiddenError, InvalidTokenVersionError, RevokedTokenError
from app.modules.users.contracts.dtos import FullUserInfoDTO
from app.modules.users.exceptions import UserBlockedError, UserClosedError
from tests.factories.refresh_token import RefreshTokensFactory
from tests.factories.user import UsersFactory


class TestLoginUserCase:
    """Тестовый кейс по входу в аккаунт пользователя"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_login_user_good(
        self, mocker: MockerFixture, mock_auth_queries, mock_manage_token_case, login_user_mock_case
    ):
        user = UsersFactory()
        mock_auth_queries.select_user_id_pass_role_by_email.return_value = {
            'password_hash': user.password_hash,
            'user_id': user.user_id,
            'role': user.role,
            'closed_at': user.closed_at,
            'blocked_at': user.blocked_at,
        }

        mock_verify_pass = mocker.patch(
            'app.modules.auth.service.use_cases.verify_pass', return_value='hashed_password'
        )

        mock_manage_token_case.encode_access_token.return_value = 'access_token'
        mock_manage_token_case.encode_refresh_token.return_value = 'refresh_token'

        result = await login_user_mock_case.login_user(user.email, user.password_hash)

        assert isinstance(result, TokenInfoDTO)
        mock_manage_token_case.encode_access_token.assert_called_once()
        access_args = mock_manage_token_case.encode_access_token.call_args.args
        assert isinstance(access_args[0], dict)
        mock_manage_token_case.encode_refresh_token.assert_awaited_once()
        refresh_args = mock_manage_token_case.encode_refresh_token.await_args.args
        assert isinstance(refresh_args[0], dict)
        mock_verify_pass.assert_called_once_with(user.password_hash, user.password_hash)

    @pytest.mark.parametrize(
        'exc_type, is_block, is_close',
        [
            (UserClosedError, False, True),
            (UserBlockedError, True, False),
        ],
        ids=[
            'closed_error',
            'blocked_error',
        ],
    )
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_login_user_bad(
        self,
        mocker: MockerFixture,
        mock_auth_queries,
        is_block,
        is_close,
        exc_type,
        mock_manage_token_case,
        login_user_mock_case,
    ):
        user = UsersFactory(block=is_block, close=is_close)

        mock_auth_queries.select_user_id_pass_role_by_email.return_value = {
            'password_hash': user.password_hash,
            'user_id': user.user_id,
            'role': user.role,
            'closed_at': user.closed_at,
            'blocked_at': user.blocked_at,
        }

        mock_verify_pass = mocker.patch(
            'app.modules.auth.service.use_cases.verify_pass',
        )

        with pytest.raises(exc_type):
            await login_user_mock_case.login_user(user.email, user.password_hash)

        mock_auth_queries.select_user_id_pass_role_by_email.assert_awaited_once_with(user.email)
        mock_manage_token_case.encode_access_token.assert_not_called()
        mock_manage_token_case.encode_refresh_token.assert_not_awaited()
        mock_verify_pass.assert_not_called()


class TestLogoutUserCase:
    """Тестовый кейс по выходу пользователя из аккаунта"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_logout_user_device_good(
        self,
        mocker: MockerFixture,
        mock_auth_commands,
        mock_current_user_redis_commands,
        mock_token_config,
        logout_user_mock_case,
    ):
        user = UsersFactory()
        mock_token_config.REFRESH_TOKEN_AUDIENCE = 'refresh_api'

        await logout_user_mock_case.logout_user_device(FullUserInfoDTO.model_validate(user))

        mock_auth_commands.alter_user_refresh_tokens_revoked_param.assert_awaited_once_with(
            user.user_id, mock_token_config.REFRESH_TOKEN_AUDIENCE
        )
        mock_current_user_redis_commands.delete_current_user.assert_awaited_once_with(user.user_id)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_logout_all_user_devices_good(
        self, mock_auth_commands, mock_current_user_redis_commands, logout_user_mock_case
    ):
        user = UsersFactory()

        await logout_user_mock_case.logout_all_user_devices(FullUserInfoDTO.model_validate(user))

        mock_auth_commands.alter_all_user_refresh_tokens_revoked_param.assert_awaited_once_with(
            user.user_id
        )
        mock_current_user_redis_commands.delete_current_user.assert_awaited_once_with(user.user_id)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_logout_all_user_devices_by_id_good(
        self, mock_auth_commands, mock_current_user_redis_commands, logout_user_mock_case
    ):
        user = UsersFactory()

        await logout_user_mock_case.logout_all_user_devices_by_id(user.user_id)

        mock_auth_commands.alter_all_user_refresh_tokens_revoked_param.assert_awaited_once_with(
            user.user_id
        )
        mock_current_user_redis_commands.delete_current_user.assert_awaited_once_with(user.user_id)


class TestRefreshUserCase:
    """Тестирование кейса по обновлению refresh токена"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_refresh_good(
        self,
        mock_manage_token_case,
        mock_token_config,
        mock_auth_queries,
        mock_current_user_redis_commands,
        refresh_user_mock_case,
        mock_auth_commands,
    ):
        token = 'jhfqleyfqf;lqngn;gqlkg'
        version = 1
        refresh_token = RefreshTokensFactory()
        user = UsersFactory()

        mock_token_config.REFRESH_TOKEN_VERSION = 1

        mock_manage_token_case.decode_refresh_token.return_value = {
            'sub': refresh_token.user_id,
            'version': version,
            'jti': refresh_token.refresh_token_id,
        }

        mock_auth_queries.select_refresh_token_revoked_by_id.return_value = refresh_token.revoked_at

        mock_current_user_redis_commands.get_current_user.return_value = user

        mock_manage_token_case.encode_access_token.return_value = 'access_token'
        mock_manage_token_case.encode_refresh_token.return_value = 'refresh_token'

        result = await refresh_user_mock_case.refresh(token)

        assert isinstance(result, TokenInfoDTO)
        mock_manage_token_case.decode_refresh_token.assert_called_once_with(token)
        mock_auth_queries.select_refresh_token_revoked_by_id.assert_awaited_once_with(
            refresh_token.refresh_token_id
        )
        mock_current_user_redis_commands.get_current_user.assert_awaited_once_with(
            refresh_token.user_id
        )
        mock_auth_queries.select_user_role_by_id.assert_not_awaited()
        mock_manage_token_case.encode_refresh_token.assert_awaited_once()
        refresh_args = mock_manage_token_case.encode_refresh_token.await_args.args
        assert refresh_args[0] == {
            'sub': str(refresh_token.user_id),
        }
        mock_manage_token_case.encode_access_token.assert_called_once()
        access_args = mock_manage_token_case.encode_access_token.call_args.args
        assert access_args[0] == {
            'sub': str(refresh_token.user_id),
            'role': user.role,
        }
        mock_auth_commands.alter_refresh_token_revoked_param.assert_awaited_once_with(
            refresh_token.refresh_token_id
        )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_refresh_version_bad(
        self,
        mock_manage_token_case,
        mock_token_config,
        refresh_user_mock_case,
        mock_auth_queries,
        mock_current_user_redis_commands,
        mock_auth_commands,
    ):
        token = 'gnjiwrgghqgv9u7qvhonq'
        refresh_token = RefreshTokensFactory()
        version = 0

        mock_token_config.REFRESH_TOKEN_VERSION = 1

        mock_manage_token_case.decode_refresh_token.return_value = {
            'sub': refresh_token.user_id,
            'version': version,
            'jti': refresh_token.refresh_token_id,
        }

        with pytest.raises(InvalidTokenVersionError):
            await refresh_user_mock_case.refresh(token)

        mock_manage_token_case.decode_refresh_token.assert_called_once_with(token)
        mock_auth_queries.select_refresh_token_revoked_by_id.assert_not_awaited()
        mock_current_user_redis_commands.get_current_user.assert_not_awaited()
        mock_auth_queries.select_user_role_by_id.assert_not_awaited()
        mock_manage_token_case.encode_refresh_token.assert_not_awaited()
        mock_manage_token_case.encode_access_token.assert_not_called()
        mock_auth_commands.alter_refresh_token_revoked_param.assert_not_awaited()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_refresh_revoke_bad(
        self,
        mock_manage_token_case,
        mock_token_config,
        refresh_user_mock_case,
        mock_auth_queries,
        mock_current_user_redis_commands,
        mock_auth_commands,
    ):
        token = 'gnjiwrgghqgv9u7qvhonq'
        refresh_token = RefreshTokensFactory(revoke=True)
        version = 1

        mock_token_config.REFRESH_TOKEN_VERSION = 1

        mock_manage_token_case.decode_refresh_token.return_value = {
            'sub': refresh_token.user_id,
            'version': version,
            'jti': refresh_token.refresh_token_id,
        }

        mock_auth_queries.select_refresh_token_revoked_by_id.return_value = refresh_token.revoked_at

        with pytest.raises(RevokedTokenError):
            await refresh_user_mock_case.refresh(token)

        mock_manage_token_case.decode_refresh_token.assert_called_once_with(token)
        mock_auth_queries.select_refresh_token_revoked_by_id.assert_awaited_once_with(
            refresh_token.refresh_token_id
        )
        mock_current_user_redis_commands.get_current_user.assert_not_awaited()
        mock_auth_queries.select_user_role_by_id.assert_not_awaited()
        mock_manage_token_case.encode_refresh_token.assert_not_awaited()
        mock_manage_token_case.encode_access_token.assert_not_called()
        mock_auth_commands.alter_refresh_token_revoked_param.assert_not_awaited()


class TestShowCurrentUserCase:
    """Тестовый кейс по показу текущего пользователя"""

    @pytest.mark.parametrize(
        'is_standard, is_admin, is_vip',
        [
            (True, None, None),
            (None, True, None),
            (None, None, None),
        ],
        ids=[
            'standard',
            'admin',
            'vip',
        ],
    )
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_current_good(
        self,
        mocker: MockerFixture,
        mock_manage_token_case,
        mock_auth_queries,
        mock_current_user_redis_commands,
        show_current_user_mock_case,
        is_vip,
        is_admin,
        is_standard,
    ):
        token = 'nfjgorg87ghqupbur'
        refresh_token = RefreshTokensFactory()
        user = UsersFactory(admin=is_admin, vip=is_vip)

        mock_manage_token_case.decode_access_token.return_value = {
            'sub': refresh_token.user_id,
            'role': user.role,
        }

        mock_auth_queries.select_not_revoked_tokens_by_user_id.return_value = mocker.Mock()

        mock_current_user_redis_commands.get_current_user.return_value = user

        result = await show_current_user_mock_case._current(token, is_admin, is_vip)

        assert isinstance(result, FullUserInfoDTO)
        mock_manage_token_case.decode_access_token.assert_called_once_with(token)
        mock_auth_queries.select_not_revoked_tokens_by_user_id.assert_awaited_once_with(
            refresh_token.user_id
        )
        mock_current_user_redis_commands.get_current_user.assert_awaited_once_with(
            refresh_token.user_id
        )
        mock_auth_queries.select_user_by_id.assert_not_awaited()
        mock_current_user_redis_commands.set_current_user.assert_not_awaited()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_current_revoke_bad(
        self,
        mock_auth_queries,
        mock_manage_token_case,
        show_current_user_mock_case,
        mock_current_user_redis_commands,
    ):
        token = 'nfjgorg87ghqupbur'
        refresh_token = RefreshTokensFactory()
        user = UsersFactory()

        mock_manage_token_case.decode_access_token.return_value = {
            'sub': refresh_token.user_id,
            'role': user.role,
        }

        mock_auth_queries.select_not_revoked_tokens_by_user_id.return_value = None

        with pytest.raises(RevokedTokenError):
            await show_current_user_mock_case._current(token)

        mock_manage_token_case.decode_access_token.assert_called_once_with(token)
        mock_auth_queries.select_not_revoked_tokens_by_user_id.assert_awaited_once_with(
            refresh_token.user_id
        )
        mock_current_user_redis_commands.get_current_user.assert_not_awaited()
        mock_auth_queries.select_user_by_id.assert_not_awaited()
        mock_current_user_redis_commands.set_current_user.assert_not_awaited()

    @pytest.mark.parametrize(
        'is_admin, is_vip',
        [
            (True, None),
            (None, True),
        ],
        ids=[
            'not_admin',
            'not_vip',
        ],
    )
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_current_role_bad(
        self,
        mocker: MockerFixture,
        mock_auth_queries,
        mock_current_user_redis_commands,
        mock_manage_token_case,
        show_current_user_mock_case,
        is_vip,
        is_admin,
    ):
        token = 'nfjgorg87ghqupbur'
        refresh_token = RefreshTokensFactory()
        user = UsersFactory()

        mock_manage_token_case.decode_access_token.return_value = {
            'sub': refresh_token.user_id,
            'role': user.role,
        }

        mock_auth_queries.select_not_revoked_tokens_by_user_id.return_value = mocker.Mock()

        mock_current_user_redis_commands.get_current_user.return_value = user

        with pytest.raises(ForbiddenError):
            await show_current_user_mock_case._current(token, is_admin, is_vip)

        mock_manage_token_case.decode_access_token.assert_called_once_with(token)
        mock_auth_queries.select_not_revoked_tokens_by_user_id.assert_awaited_once_with(
            refresh_token.user_id
        )
        mock_current_user_redis_commands.get_current_user.assert_awaited_once_with(
            refresh_token.user_id
        )
        mock_auth_queries.select_user_by_id.assert_not_awaited()
        mock_current_user_redis_commands.set_current_user.assert_not_awaited()
