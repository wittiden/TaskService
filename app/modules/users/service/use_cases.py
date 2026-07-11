from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.common.enums.user import UserRoleEnum
from app.common.security.pass_utils import hash_pass
from app.modules.auth.service.use_cases import LogoutUserCase
from app.modules.users.contracts.dtos import SecurityUserInfoDTO, FullUserInfoDTO
from app.modules.users.exceptions import InvalidUserDataError, UserNotFoundError, UserAlreadyBlockedError, \
    UserAlreadyUnblockedError
from app.modules.users.repository.commands import UserCommandsRepository
from app.modules.users.repository.queries import UserQueriesRepository
from app.modules.users.service.guards import UserGuards


class CreateUserCase:
    """Кейс по созданию пользователя"""

    def __init__(self, user_commands: UserCommandsRepository) -> None:
        self._user_commands = user_commands

    async def _create(self, name: str, email: str, password: str, role: UserRoleEnum) -> SecurityUserInfoDTO:
        password_hash = hash_pass(password)

        try:
            user = await self._user_commands.insert_user_data(name, email, password_hash, role)
        except IntegrityError:
            raise InvalidUserDataError('User cant create due to invalid data')
        user = UserGuards.require_user_exist(user)

        return SecurityUserInfoDTO.model_validate(user)

    async def create_standard(self, name: str, email: str, password: str) -> SecurityUserInfoDTO:
        return await self._create(name, email, password, UserRoleEnum.STANDARD)

    async def create_vip(self, name: str, email: str, password: str) -> SecurityUserInfoDTO:
        return await self._create(name, email, password, UserRoleEnum.VIP)

    async def create_admin(self, name: str, email: str, password: str) -> SecurityUserInfoDTO:
        return await self._create(name, email, password, UserRoleEnum.ADMIN)


class UpdateUserCase:
    """Кейс по обновлению информации пользователя"""


class DeleteUserCase:
    """Кейс по удалению пользователя"""

    def __init__(self, user_commands: UserCommandsRepository, logout_user_case: LogoutUserCase) -> None:
        self._user_commands = user_commands
        self._logout_user_case = logout_user_case

    async def close_my_account(self, current_user: FullUserInfoDTO) -> None:
        await self._user_commands.alter_user_closed_param(current_user.user_id)
        await self._logout_user_case.logout_all_user_devices(current_user)

    async def delete_user_account(self, user_id: UUID) -> None:
        deleted_obj_id = await self._user_commands.delete_closed_user_by_id(user_id)
        if deleted_obj_id is None:
            raise UserNotFoundError('User with spec parameters not found for deletion')
        await self._logout_user_case.logout_all_user_devices_by_id(user_id)


class ManageUserCase:
    """Кейс по менедженгу пользователей"""

    def __init__(self, user_commands: UserCommandsRepository, logout_user_case: LogoutUserCase, user_queries: UserQueriesRepository) -> None:
        self._user_commands = user_commands
        self._logout_user_case = logout_user_case
        self._user_queries = user_queries

    async def block_user(self, user_id: UUID) -> FullUserInfoDTO:
        blocked_at = await self._user_queries.select_user_block_param(user_id)
        if blocked_at:
            raise UserAlreadyBlockedError('User account blocked before')

        user = await self._user_commands.alter_block_user_by_id(user_id)
        user = UserGuards.require_user_exist(user)

        await self._logout_user_case.logout_all_user_devices_by_id(user_id)

        return FullUserInfoDTO.model_validate(user)

    async def unblock_user(self, user_id: UUID) -> FullUserInfoDTO:
        blocked_at = await self._user_queries.select_user_block_param(user_id)
        if blocked_at is None:
            raise UserAlreadyUnblockedError('User account unblocked before')

        user = await self._user_commands.alter_unblock_user_by_id(user_id)
        user = UserGuards.require_user_exist(user)

        return FullUserInfoDTO.model_validate(user)


class ShowUserCase: 
    """Кейс по показу информации пользователей"""

    def __init__(self, user_queries: UserQueriesRepository) -> None:
        self._user_queries = user_queries

    async def show_me(self, current_user: FullUserInfoDTO) -> SecurityUserInfoDTO:
        return SecurityUserInfoDTO.model_validate(current_user)

    async def show_user_by_id(self, user_id: UUID) -> FullUserInfoDTO:
        user = await self._user_queries.select_user_by_id(user_id)
        user = UserGuards.require_user_exist(user)

        return FullUserInfoDTO.model_validate(user)

    async def show_users(self, offset: int = 0, limit: int = 100) -> list[FullUserInfoDTO]:
        users = await self._user_queries.select_users(offset, limit)

        return [FullUserInfoDTO.model_validate(user) for user in users]
