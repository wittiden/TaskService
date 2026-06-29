from datetime import datetime, UTC, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.common.enums.users import UserRoleEnum
from app.common.security.pass_utils import hash_pass, same_pass
from app.infrastructure.database.models import UserModel
from app.infrastructure.redis.repositories.current_user import RedisCurrentUserRepository
from app.modules.auth.service.use_cases import AuthUserCase
from app.modules.users.contracts.dtos import SecurityUserInfoDTO, UserInfoDTO
from app.modules.users.exceptions import EmailIsExistError, UserDeletionGracePeriodError, UserAlreadyClosedError, \
    UserAlreadyBlockedError, UserAlreadyUnBlockedError, UserNotMarkedForDeletion
from app.modules.users.repository.commands import UserCommandsRepository
from app.modules.users.repository.queries import UserQueriesRepository
from app.modules.users.service.guard_config import UserGuardConfig
from app.modules.users.service.guards import UserGuards


class CreateUserCase:
    """Кейс по созданию пользователей"""

    def __init__(self, user_commands: UserCommandsRepository) -> None:
        self._user_commands = user_commands

    async def _create(self, name: str, email: str, password: str, role: UserRoleEnum) -> SecurityUserInfoDTO:
        password_hash = hash_pass(password)
        created_at = datetime.now(UTC)

        user = UserModel(name=name, email=email, password_hash=password_hash, role=role, created_at=created_at)

        try:
            user = await self._user_commands.insert_user_data(user)
        except IntegrityError:
            raise EmailIsExistError('User email must be unique')
        user = UserGuards.require_user_is_exist(user)

        return SecurityUserInfoDTO.model_validate(user)

    async def create_standard_user(self, name: str, email: str, password: str) -> SecurityUserInfoDTO:
        user = await self._create(name, email, password, UserRoleEnum.STANDARD_USER)
        return user

    async def create_vip_user(self, name: str, email: str, password: str) -> SecurityUserInfoDTO:
        user = await self._create(name, email, password, UserRoleEnum.VIP_USER)
        return user

    async def create_admin(self, name: str, email: str, password: str) -> SecurityUserInfoDTO:
        user = await self._create(name, email, password, UserRoleEnum.ADMIN)
        return user


class UpdateUserCase:
    """Кейс по обновлению данных пользователей"""

    def __init__(self, user_commands: UserCommandsRepository, user_queries: UserQueriesRepository, redis_current_user: RedisCurrentUserRepository) -> None:
        self._user_commands = user_commands
        self._user_queries = user_queries
        self._redis_current_user = redis_current_user

    async def partial_update_user_data(self, current_user: UserInfoDTO, new_data: dict[str, Any]) -> SecurityUserInfoDTO:
        if all(x is None for x in new_data.values()):
            return SecurityUserInfoDTO.model_validate(current_user)

        columns = await self._user_queries.select_user_id_and_pass(current_user.user_id)
        columns = UserGuards.require_columns_is_exist(columns)

        if columns['blocked_at'] is not None:
            raise UserAlreadyBlockedError('User already blocked error')
        if columns['closed_at'] is not None:
            raise UserAlreadyClosedError('User already closed error')

        if 'password' in new_data:
            same_pass(new_data['password'], columns['password_hash'])
            new_data['password_hash'] = hash_pass(new_data.pop('password'))

        new_data['updated_at'] = datetime.now(UTC)

        updated_user_model = await self._user_commands.alter_user_info_by_id(current_user.user_id, new_data)
        await self._redis_current_user.set_current_user(UserInfoDTO.model_validate(updated_user_model))

        return SecurityUserInfoDTO.model_validate(updated_user_model)


class DeleteUserCase:
    """Кейс по удалению пользователей"""

    def __init__(self, user_commands: UserCommandsRepository, user_queries: UserQueriesRepository, user_guard_config: UserGuardConfig, auth_user_case: AuthUserCase, redis_current_user: RedisCurrentUserRepository) -> None:
        self._user_commands = user_commands
        self._user_queries = user_queries
        self._user_guard_config = user_guard_config
        self._auth_user_case = auth_user_case
        self._redis_current_user = redis_current_user

    async def close_user(self, current_user: UserInfoDTO) -> None:
        columns = await self._user_queries.select_user_id_and_closed_at(current_user.user_id)
        columns = UserGuards.require_columns_is_exist(columns)

        if columns['closed_at'] is not None:
            raise UserAlreadyClosedError('User already closed error')

        new_data = {
            'closed_at': datetime.now(UTC)
        }
        updated_user_model = await self._user_commands.alter_user_info_by_id(current_user.user_id, new_data)
        updated_user_model = UserGuards.require_user_is_exist(updated_user_model)
        user_dto = UserInfoDTO.model_validate(updated_user_model)

        await self._auth_user_case.logout(user_dto)
        await self._redis_current_user.delete_current_user_from_redis(current_user.user_id)


    async def delete_user(self, user_id: UUID) -> None:
        now = datetime.now(UTC)

        obj = await self._user_queries.select_user_by_id(user_id)
        obj = UserGuards.require_user_is_exist(obj)

        if obj.blocked_at is None or obj.closed_at is None:
            raise UserNotMarkedForDeletion('Cant delete without special mark')

        if not now >= obj.closed_at + timedelta(days=self._user_guard_config.ACCOUNT_DELETION_GRACE_DAYS)\
                or now >= obj.blocked_at + timedelta(days=self._user_guard_config.ACCOUNT_DELETION_GRACE_DAYS):
            raise UserDeletionGracePeriodError('User deletion grace period error')

        await self._redis_current_user.delete_current_user_from_redis(obj.user_id)
        await self._user_commands.delete_user(obj)


class ShowUserCase:
    """Кейс по показу данных пользователей"""

    def __init__(self, user_queries: UserQueriesRepository) -> None:
        self._user_queries = user_queries

    async def show_users(self, limit: int = 100, offset: int = 0) -> list[UserInfoDTO]:
        objs = await self._user_queries.select_users(limit, offset)
        return [UserInfoDTO.model_validate(obj) for obj in objs]

    async def show_my_user(self, current_user: UserInfoDTO) -> SecurityUserInfoDTO:
        return SecurityUserInfoDTO.model_validate(current_user)

    async def show_user_by_id(self, user_id: UUID) -> UserInfoDTO:
        obj = await self._user_queries.select_user_by_id(user_id)
        obj = UserGuards.require_user_is_exist(obj)
        return UserInfoDTO.model_validate(obj)


class ManageUserCase:
    """Кейс по менедженгу данных пользователей"""

    def __init__(self, user_commands: UserCommandsRepository, user_queries: UserQueriesRepository, auth_user_case: AuthUserCase, redis_current_user: RedisCurrentUserRepository) -> None:
        self._user_commands = user_commands
        self._user_queries = user_queries
        self._auth_user_case = auth_user_case
        self._redis_current_user = redis_current_user

    async def block_user(self, user_id: UUID) -> None:
        now = datetime.now(UTC)

        obj = await self._user_queries.select_user_by_id(user_id)
        obj = UserGuards.require_user_is_exist(obj)

        if obj.blocked_at is not None:
            raise UserAlreadyBlockedError('User already blocked error')

        new_data = {
            'blocked_at': now
        }
        user = await self._user_commands.alter_user_info(obj, new_data)
        user_dto = UserInfoDTO.model_validate(user)
        await self._auth_user_case.logout(user_dto)
        await self._redis_current_user.delete_current_user_from_redis(user_id)

    async def unblock_user(self, user_id: UUID) -> None:
        obj = await self._user_queries.select_user_by_id(user_id)
        obj = UserGuards.require_user_is_exist(obj)

        if obj.blocked_at is None:
            raise UserAlreadyUnBlockedError('User already unblocked error')

        new_data = {
            'blocked_at': None
        }
        user = await self._user_commands.alter_user_info(obj, new_data)
        user_dto = UserInfoDTO.model_validate(user)
        await self._redis_current_user.set_current_user(user_dto)
