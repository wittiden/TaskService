from datetime import datetime

import pytest
from pytest_mock import MockerFixture

from app.infrastructure.database.models import UserModel
from app.infrastructure.redis.repositories.current_user import RedisCurrentUserRepository
from app.modules.auth.service.use_cases import AuthUserCase
from app.modules.users.contracts.dtos import SecurityUserInfoDTO, UserInfoDTO
from app.modules.users.repository.commands import UserCommandsRepository
from app.modules.users.repository.queries import UserQueriesRepository
from app.modules.users.service.use_cases import CreateUserCase, UpdateUserCase, DeleteUserCase
from tests.factories.user import UserFactory


class TestCreateUserCase:
    """Тестирование кейса по созданию пользователей"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'admin_trait, vip_trait',
        [
            (False, False),
            (True, False),
            (False, True)
        ],
        ids=[
            'standard_user',
            'admin',
            'vip_user'
        ]
    )
    async def test_create_user_good(self, mocker: MockerFixture, user_commands: UserCommandsRepository, create_user_case: CreateUserCase, admin_trait, vip_trait):
        row_password = 'row_password'
        password_hash = 'hashed_password'
        mock_hash = mocker.patch(
            'app.modules.users.service.use_cases.hash_pass',
            return_value=password_hash
        )

        user = UserFactory(
            password_hash=password_hash,
            admin=admin_trait,
            vip=vip_trait,
        )
        user_model = UserModel(
            user_id=user.user_id,
            name=user.name,
            email=user.email,
            password_hash=user.password_hash,
            role=user.role,
            created_at=user.created_at,
        )
        user_commands.insert_user_data.return_value = user_model

        result = await create_user_case.create_standard_user(
            user.name,
            user.email,
            row_password,
        )

        assert isinstance(result, SecurityUserInfoDTO)
        assert user.name == result.name
        assert user.email == result.email
        assert user.role == result.role
        mock_hash.assert_called_once_with(row_password)
        user_commands.insert_user_data.assert_awaited_once()
        args = user_commands.insert_user_data.await_args.args
        assert isinstance(args[0], UserModel)


class TestUpdateUserCase:
    """Класс для тестирования кейса обновления пользователей"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'new_data',
        [
            ({
            'name': 'new_name',
            'email': 'new_email@example.com',
            'password': 'row_password',
            }),
            ({
            'name': None,
            'email': None,
            'password': None,
            })
        ],
        ids=[
            'new_data_with_values',
            'empty_new_data'
        ]
    )
    async def test_partial_update_user_data_good(self, mocker: MockerFixture, user_queries: UserQueriesRepository, user_commands: UserCommandsRepository, update_user_case: UpdateUserCase, redis_current_user: RedisCurrentUserRepository, new_data):
        row_password = 'row_password'
        password_hash = 'hashed_password'
        user = UserFactory(
            password_hash=password_hash
        )

        user_queries.select_user_id_and_pass.return_value = {
            'user_id': user.user_id,
            'password_hash': password_hash,
            'blocked_at': user.blocked_at,
            'closed_at': user.closed_at,
        }

        mock_same_pass = mocker.patch(
            'app.modules.users.service.use_cases.same_pass'
        )
        mock_hash_pass = mocker.patch(
            'app.modules.users.service.use_cases.hash_pass',
            return_value=password_hash
        )

        user_model = UserModel(
            user_id=user.user_id,
            name=new_data['name'],
            email=new_data['email'],
            password_hash=user.password_hash,
            role=user.role,
            created_at=user.created_at,
        )

        user_commands.alter_user_info_by_id.return_value = user_model
        result = await update_user_case.partial_update_user_data(
            UserInfoDTO.model_validate(user),
            new_data
        )

        assert isinstance(result, SecurityUserInfoDTO)
        if any(x is not None for x in new_data.values()):
            assert result.name == new_data['name']
            assert result.email == new_data['email']
            assert result.role == user.role
            mock_same_pass.assert_called_once_with(row_password, password_hash)
            mock_hash_pass.assert_called_once_with(row_password)
            user_queries.select_user_id_and_pass.assert_awaited_once_with(user.user_id)
            user_commands.alter_user_info_by_id.assert_awaited_once_with(user.user_id, new_data)
            redis_current_user.set_current_user.assert_awaited_once_with(UserInfoDTO.model_validate(user_model))


class TestDeleteUserCase:
    """Тестовый кейс по удалению пользователей"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_close_user_good(self, user_queries: UserQueriesRepository, user_commands: UserCommandsRepository, auth_user: AuthUserCase, redis_current_user: RedisCurrentUserRepository, delete_user_case: DeleteUserCase):
        user = UserFactory()

        user_queries.select_user_id_and_closed_at.return_value = {
            'user_id': user.user_id,
            'closed_at': user.closed_at,
        }

        user_commands.alter_user_info_by_id.return_value = UserModel(
            user_id=user.user_id,
            name=user.name,
            email=user.email,
            password_hash=user.password_hash,
            role=user.role,
            created_at=user.created_at,
            closed_at=user.closed_at
        )

        result = await delete_user_case.close_user(
            UserInfoDTO.model_validate(user)
        )

        assert result is None
        user_queries.select_user_id_and_closed_at.assert_awaited_once_with(user.user_id)
        user_commands.alter_user_info_by_id.assert_awaited_once()
        args = user_commands.alter_user_info_by_id.await_args.args
        assert args[0] == user.user_id
        assert isinstance(args[1]['closed_at'], datetime)
        auth_user.logout.assert_awaited_once_with(UserInfoDTO.model_validate(user))
        redis_current_user.delete_current_user_from_redis.assert_awaited_once_with(user.user_id)
