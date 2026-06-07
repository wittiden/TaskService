from datetime import datetime, UTC
from sqlalchemy.exc import IntegrityError

from app.common.emums.users import UserRoleEnum
from app.common.security.pass_utils import hash_pass
from app.infrastructure.database.models import UserModel
from app.modules.users.contracts.dtos import SecurityUserInfoDTO
from app.modules.users.exceptions import EmailIsExistError
from app.modules.users.repository.commands import UserCommandsRepository
from app.modules.users.repository.queries import UserQueriesRepository
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


class DeleteUserCase:
    """Кейс по удалению пользователей"""


class ShowUserCase:
    """Кейс по показу данных пользователей"""

    def __init__(self, user_queries: UserQueriesRepository) -> None:
        self._user_queries = user_queries


class ManageUserCase:
    """"""
