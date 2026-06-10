from datetime import datetime, UTC, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.common.enums.users import UserRoleEnum
from app.common.security.pass_utils import hash_pass, verify_pass
from app.infrastructure.database.models import UserModel
from app.modules.auth.service.use_cases import AuthUserCase
from app.modules.users.contracts.dtos import SecurityUserInfoDTO, FullUserInfoDTO
from app.modules.users.exceptions import EmailIsExistError, UserDeletionGracePeriodError, UserAlreadyClosedError, \
    UserAlreadyBlockedError, UserAlreadyUnBlockedError, SamePasswordsError
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
        user = UserGuards.require_user_is_exist(user)

        try:
            user = await self._user_commands.insert_user_data(user)
        except IntegrityError:
            raise EmailIsExistError('User email must be unique')

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

    def __init__(self, user_commands: UserCommandsRepository, user_queries: UserQueriesRepository) -> None:
        self._user_commands = user_commands
        self._user_queries = user_queries

    async def partial_user_data(self, current_user: UserModel, new_data: dict[str, Any]) -> SecurityUserInfoDTO:
        now = datetime.now(UTC)

        current_user = UserGuards.require_user_is_exist(current_user)

        if 'password' in new_data:
            if verify_pass(new_data['password'], current_user.password_hash):
                raise SamePasswordsError('Same passwords error')

            new_data['password_hash'] = hash_pass(new_data.pop('password'))

        if all(x is None for x in new_data.values()):
            return SecurityUserInfoDTO.model_validate(current_user)

        new_data['updated_at'] = now

        user = await self._user_commands.alter_user_info(current_user, new_data)
        return SecurityUserInfoDTO.model_validate(user)


class DeleteUserCase:
    """Кейс по удалению пользователей"""

    def __init__(self, user_commands: UserCommandsRepository, user_queries: UserQueriesRepository, user_guard_config: UserGuardConfig, auth_user_case: AuthUserCase) -> None:
        self._user_commands = user_commands
        self._user_queries = user_queries
        self._user_guard_config = user_guard_config
        self._auth_user_case = auth_user_case

    async def close_user(self, current_user: UserModel) -> None:
        now = datetime.now(UTC)

        current_user = UserGuards.require_user_is_exist(current_user)

        if current_user.closed_at is not None:
            raise UserAlreadyClosedError('User already closed error')

        new_data = {
            'closed_at': now
        }
        await self._user_commands.alter_user_info(current_user, new_data)
        await self._auth_user_case.logout(current_user)


    async def delete_user(self, user_id: UUID) -> None:
        now = datetime.now(UTC)

        obj = await self._user_queries.select_user_by_id(user_id)
        obj = UserGuards.require_user_is_exist(obj)

        if not now >= obj.closed_at + timedelta(days=self._user_guard_config.ACCOUNT_DELETION_GRACE_DAYS)\
                or now >= obj.blocked_at + timedelta(days=self._user_guard_config.ACCOUNT_DELETION_GRACE_DAYS):
            raise UserDeletionGracePeriodError('User deletion grace period error')

        await self._user_commands.delete_user(obj)


class ShowUserCase:
    """Кейс по показу данных пользователей"""

    def __init__(self, user_queries: UserQueriesRepository) -> None:
        self._user_queries = user_queries

    async def show_users(self, limit: int = 100, offset: int = 0) -> list[FullUserInfoDTO]:
        objs = await self._user_queries.select_users(limit, offset)
        return [FullUserInfoDTO.model_validate(obj) for obj in objs]

    async def show_my_user(self, current_user: UserModel) -> SecurityUserInfoDTO:
        obj = await self._user_queries.select_user(current_user)
        obj = UserGuards.require_user_is_exist(obj)
        return SecurityUserInfoDTO.model_validate(obj)

    async def show_user_by_id(self, user_id: UUID) -> FullUserInfoDTO:
        obj = await self._user_queries.select_user_by_id(user_id)
        obj = UserGuards.require_user_is_exist(obj)
        return FullUserInfoDTO.model_validate(obj)

    async def show_user_by_email(self, email: str) -> SecurityUserInfoDTO:
        obj = await self._user_queries.select_user_by_email(email)
        obj = UserGuards.require_user_is_exist(obj)
        return SecurityUserInfoDTO.model_validate(obj)

class ManageUserCase:
    """Кейс по менедженгу данных пользователей"""

    def __init__(self, user_commands: UserCommandsRepository, user_queries: UserQueriesRepository, auth_user_case: AuthUserCase) -> None:
        self._user_commands = user_commands
        self._user_queries = user_queries
        self._auth_user_case = auth_user_case

    async def block_user(self, user_id: UUID) -> None:
        now = datetime.now(UTC)

        obj = await self._user_queries.select_user_by_id(user_id)
        obj = UserGuards.require_user_is_exist(obj)

        if obj.blocked_at is not None:
            raise UserAlreadyBlockedError('User already blocked error')

        new_data = {
            'blocked_at': now
        }
        await self._user_commands.alter_user_info(obj, new_data)
        await self._auth_user_case.logout(obj)

    async def unblock_user(self, user_id: UUID) -> None:
        obj = await self._user_queries.select_user_by_id(user_id)
        obj = UserGuards.require_user_is_exist(obj)

        if obj.blocked_at is None:
            raise UserAlreadyUnBlockedError('User already unblocked error')

        new_data = {
            'blocked_at': None
        }
        await self._user_commands.alter_user_info(obj, new_data)
