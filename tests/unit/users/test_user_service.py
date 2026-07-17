import pytest
from pytest_mock import MockerFixture
from sqlalchemy.exc import IntegrityError

from app.infrastructure.database.model import UserModel
from app.modules.users.contracts.dtos import FullUserInfoDTO, SecurityUserInfoDTO
from app.modules.users.exceptions import (
    InvalidUserDataError,
    UserAlreadyBlockedError,
    UserAlreadyUnblockedError,
    UserEmailExistError,
    UserNotFoundError,
)
from tests.factories.user import UsersFactory


class TestCreateUserCase:
    """Класс по тестированию кейса по созданию пользователей"""

    @pytest.mark.parametrize(
        'is_standard, is_admin, is_vip',
        [(True, False, False), (False, True, False), (False, False, True)],
        ids=['standard', 'admin', 'vip'],
    )
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_user_good(
        self,
        mocker: MockerFixture,
        mock_user_commands,
        create_user_mock_case,
        is_standard,
        is_admin,
        is_vip,
    ):
        user = UsersFactory.build(admin=is_admin, vip=is_vip)

        mock_hash_pass = mocker.patch(
            'app.modules.users.service.use_cases.hash_pass',
            return_value='hashed_password',
        )

        user_model = UserModel(
            user_id=user.user_id,
            name=user.name,
            email=user.email,
            password_hash='hashed_password',
            role=user.role,
            created_at=user.created_at,
            closed_at=user.closed_at,
            updated_at=user.updated_at,
            blocked_at=user.blocked_at,
        )
        mock_user_commands.insert_user_data.return_value = user_model

        result = await create_user_mock_case._create(
            user.name, user.email, user.password_hash, user.role
        )

        mock_hash_pass.assert_called_once_with(user.password_hash)
        mock_user_commands.insert_user_data.assert_awaited_once_with(
            user.name, user.email, 'hashed_password', user.role
        )
        assert isinstance(result, SecurityUserInfoDTO)
        assert result.name == user.name
        assert result.email == user.email
        assert result.role == user.role

    @pytest.mark.parametrize(
        'is_standard, is_admin, is_vip',
        [
            (True, False, False),
            (False, True, False),
            (False, False, True),
        ],
        ids=[
            'standard',
            'admin',
            'vip',
        ],
    )
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_user_bad(
        self,
        mocker: MockerFixture,
        mock_user_commands,
        create_user_mock_case,
        is_standard,
        is_admin,
        is_vip,
    ):
        user = UsersFactory.build(admin=is_admin, vip=is_vip)

        mock_hash_pass = mocker.patch(
            'app.modules.users.service.use_cases.hash_pass',
            return_value='hashed_password',
        )

        mock_user_commands.insert_user_data.side_effect = IntegrityError(
            statement=None, params=None, orig=Exception('duplicate key')
        )

        with pytest.raises(InvalidUserDataError):
            await create_user_mock_case._create(
                user.name, user.email, user.password_hash, user.role
            )

        mock_hash_pass.assert_called_once_with(user.password_hash)
        mock_user_commands.insert_user_data.assert_awaited_once_with(
            user.name, user.email, 'hashed_password', user.role
        )


class TestUpdateUserCase:
    """Класс по тестированию кейса по обновлению данных пользователей"""

    @pytest.mark.parametrize(
        'new_params',
        [
            (None),
            (
                {
                    'name': 'new_name',
                    'email': 'new_email@example.com',
                    'password': 'nf2ioug2753hg2p2u52gf3ngo22',
                }
            ),
        ],
        ids=['without_new_params', 'with_new_params'],
    )
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_user_params_good(
        self,
        mocker: MockerFixture,
        mock_user_commands,
        new_params,
        mock_current_user_redis_commands,
        update_user_mock_case,
        mock_create_user_audit_case,
    ):
        user = UsersFactory.build()

        if new_params is None:
            result = await update_user_mock_case.update_user_params(
                FullUserInfoDTO.model_validate(user), new_params
            )
            assert isinstance(result, SecurityUserInfoDTO)

        else:
            hashed_password = 'hashed_password'
            password = new_params['password']

            mock_hash_pass = mocker.patch(
                'app.modules.users.service.use_cases.hash_pass',
                return_value=hashed_password,
            )

            user_model = UserModel(
                user_id=user.user_id,
                name=new_params['name'],
                email=new_params['email'],
                password_hash=hashed_password,
                role=user.role,
                created_at=user.created_at,
                closed_at=user.closed_at,
                updated_at=user.updated_at,
                blocked_at=user.blocked_at,
            )

            mock_user_commands.alter_user_params.return_value = user_model

            result = await update_user_mock_case.update_user_params(
                FullUserInfoDTO.model_validate(user), new_params
            )

            assert isinstance(result, SecurityUserInfoDTO)
            mock_hash_pass.assert_called_once_with(password)
            mock_user_commands.alter_user_params.assert_awaited_once_with(user.user_id, new_params)
            mock_current_user_redis_commands.set_current_user.assert_awaited_once_with(
                FullUserInfoDTO.model_validate(user_model)
            )
            assert mock_create_user_audit_case.create_user_audit.await_count == 3
            assert result.name == new_params['name']
            assert result.email == new_params['email']

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_user_params_bad(
        self,
        mocker: MockerFixture,
        mock_user_commands,
        update_user_mock_case,
        mock_current_user_redis_commands,
        mock_create_user_audit_case,
    ):
        user = UsersFactory.build()
        new_params = {
            'name': 'new_name',
            'email': 'new_email@example.com',
            'password': 'frnjlhg2oyr814fjvw',
        }
        password = new_params['password']
        hashed_password = 'hashed_password'
        mock_hash_pass = mocker.patch(
            'app.modules.users.service.use_cases.hash_pass',
            return_value=hashed_password,
        )

        mock_user_commands.alter_user_params.side_effect = IntegrityError(
            statement=None, params=None, orig=Exception('duplicate key')
        )

        with pytest.raises(UserEmailExistError):
            await update_user_mock_case.update_user_params(
                FullUserInfoDTO.model_validate(user), new_params
            )

        mock_user_commands.alter_user_params.assert_awaited_once_with(user.user_id, new_params)
        mock_hash_pass.assert_called_once_with(password)
        mock_current_user_redis_commands.set_current_user.assert_not_awaited()
        mock_create_user_audit_case.create_user_audit.assert_not_awaited()


class TestDeleteUserCase:
    """Класс по тестированию кейса по удалению пользователей"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_close_my_account_good(
        self,
        mock_user_commands,
        mock_logout_user_case,
        delete_user_mock_case,
        mock_create_user_audit_case,
    ):
        user = UsersFactory.build(close=True)
        user_model = UserModel(
            user_id=user.user_id,
            name=user.name,
            email=user.email,
            password_hash=user.password_hash,
            role=user.role,
            created_at=user.created_at,
            closed_at=user.closed_at,
            updated_at=user.updated_at,
            blocked_at=user.blocked_at,
        )

        mock_user_commands.alter_user_closed_param.return_value = user_model

        await delete_user_mock_case.close_my_account(FullUserInfoDTO.model_validate(user))

        mock_user_commands.alter_user_closed_param.assert_awaited_with(user.user_id)
        mock_logout_user_case.logout_all_user_devices.assert_awaited_once_with(
            FullUserInfoDTO.model_validate(user)
        )
        mock_create_user_audit_case.create_user_audit.assert_called_once()
        args = mock_create_user_audit_case.create_user_audit.await_args.args
        assert args[0] == user.user_id

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_close_my_account_bad(
        self,
        mock_user_commands,
        mock_logout_user_case,
        mock_create_user_audit_case,
        delete_user_mock_case,
    ):
        user = UsersFactory.build()

        mock_user_commands.alter_user_closed_param.return_value = None

        with pytest.raises(UserNotFoundError):
            await delete_user_mock_case.close_my_account(FullUserInfoDTO.model_validate(user))

        mock_user_commands.alter_user_closed_param.assert_awaited_with(user.user_id)
        mock_logout_user_case.logout_all_user_devices.assert_not_awaited()
        mock_create_user_audit_case.create_user_audit.assert_not_awaited()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_user_account_good(
        self, mock_user_commands, mock_logout_user_case, delete_user_mock_case
    ):
        user = UsersFactory.build(close=True)

        mock_user_commands.delete_closed_user_by_id.return_value = user.user_id

        await delete_user_mock_case.delete_user_account(user.user_id)

        mock_user_commands.delete_closed_user_by_id.assert_awaited_once_with(user.user_id)
        mock_logout_user_case.logout_all_user_devices_by_id.assert_awaited_once_with(user.user_id)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_user_account_bad(
        self, mock_user_commands, mock_logout_user_case, delete_user_mock_case
    ):
        user = UsersFactory.build()
        mock_user_commands.delete_closed_user_by_id.return_value = None

        with pytest.raises(UserNotFoundError):
            await delete_user_mock_case.delete_user_account(user.user_id)

        mock_user_commands.delete_closed_user_by_id.assert_awaited_once_with(user.user_id)
        mock_logout_user_case.logout_all_user_devices_by_id.assert_not_awaited()


class TestManageUserCase:
    """Класс по тестированию кейса по менедженгу пользователей"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_block_user_good(
        self,
        mock_user_queries,
        mock_user_commands,
        mock_logout_user_case,
        manage_user_mock_case,
        mock_create_user_audit_case,
    ):
        user = UsersFactory.build(block=True)

        mock_user_queries.select_user_block_param.return_value = None

        user_model = UserModel(
            user_id=user.user_id,
            name=user.name,
            email=user.email,
            password_hash=user.password_hash,
            role=user.role,
            created_at=user.created_at,
            closed_at=user.closed_at,
            updated_at=user.updated_at,
            blocked_at=user.blocked_at,
        )
        mock_user_commands.alter_block_user_by_id.return_value = user_model

        result = await manage_user_mock_case.block_user(user.user_id)

        assert isinstance(result, FullUserInfoDTO)
        mock_user_queries.select_user_block_param.assert_awaited_once_with(user.user_id)
        mock_user_commands.alter_block_user_by_id.assert_awaited_once_with(user.user_id)
        mock_logout_user_case.logout_all_user_devices_by_id.assert_awaited_once_with(user.user_id)
        mock_create_user_audit_case.create_user_audit.assert_awaited_once()
        args = mock_create_user_audit_case.create_user_audit.await_args.args
        assert args[0] == user.user_id
        assert result.blocked_at == user.blocked_at

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_block_user_bad(
        self,
        mock_user_queries,
        mock_user_commands,
        mock_logout_user_case,
        mock_create_user_audit_case,
        manage_user_mock_case,
    ):
        user = UsersFactory.build(block=True)

        mock_user_queries.select_user_block_param.return_value = user.blocked_at

        with pytest.raises(UserAlreadyBlockedError):
            await manage_user_mock_case.block_user(user.user_id)

        mock_user_queries.select_user_block_param.assert_awaited_once_with(user.user_id)
        mock_user_commands.alter_block_user_by_id.assert_not_awaited()
        mock_logout_user_case.logout_all_user_devices_by_id.assert_not_awaited()
        mock_create_user_audit_case.create_user_audit.assert_not_awaited()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_unblock_user_good(
        self,
        mock_user_queries,
        mock_user_commands,
        manage_user_mock_case,
        mock_create_user_audit_case,
    ):
        user = UsersFactory.build(block=True)

        mock_user_queries.select_user_block_param.return_value = user.blocked_at

        user_model = UserModel(
            user_id=user.user_id,
            name=user.name,
            email=user.email,
            password_hash=user.password_hash,
            role=user.role,
            created_at=user.created_at,
            closed_at=user.closed_at,
            updated_at=user.updated_at,
            blocked_at=None,
        )
        mock_user_commands.alter_unblock_user_by_id.return_value = user_model

        result = await manage_user_mock_case.unblock_user(user.user_id)

        assert isinstance(result, FullUserInfoDTO)
        mock_user_queries.select_user_block_param.assert_awaited_once_with(user.user_id)
        mock_user_commands.alter_unblock_user_by_id.assert_awaited_once_with(user.user_id)
        mock_create_user_audit_case.create_user_audit.assert_awaited_once()
        args = mock_create_user_audit_case.create_user_audit.await_args.args
        assert args[0] == user.user_id
        assert result.blocked_at == user_model.blocked_at

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_unblock_user_bad(
        self,
        mock_user_queries,
        manage_user_mock_case,
        mock_user_commands,
        mock_create_user_audit_case,
    ):
        user = UsersFactory.build()

        mock_user_queries.select_user_block_param.return_value = user.blocked_at

        with pytest.raises(UserAlreadyUnblockedError):
            await manage_user_mock_case.unblock_user(user.user_id)

        mock_user_queries.select_user_block_param.assert_awaited_once_with(user.user_id)
        mock_user_commands.alter_unblock_user_by_id.assert_not_awaited()
        mock_create_user_audit_case.create_user_audit.assert_not_awaited()
