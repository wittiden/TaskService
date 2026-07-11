from sqlalchemy.exc import IntegrityError

from app.common.enums.user import UserRoleEnum
from app.common.security.pass_utils import hash_pass
from app.modules.auth.service.use_cases import LogoutUserCase
from app.modules.users.contracts.dtos import SecurityUserInfoDTO, FullUserInfoDTO
from app.modules.users.exceptions import InvalidUserDataError
from app.modules.users.repository.commands import UserCommandsRepository
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

    async def close_my_account(self, current_user: FullUserInfoDTO):
        await self._user_commands.alter_user_closed_param(current_user.user_id)
        await self._logout_user_case.logout_all_user_devices(current_user)

    async def delete_my_account(self):
        pass


class ManageUserCase:
    """Кейс по менедженгу пользователей"""


class ShowUserCase: 
    """Кейс по показу информации пользователей"""
