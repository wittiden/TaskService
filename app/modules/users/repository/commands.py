from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.common.enums.user import UserRoleEnum
from app.infrastructure.database.model.user import UserModel


class UserCommandsRepository:
    """Репозиторий для insert, update, delete запросов"""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

    async def insert_user_data(self, name: str, email: str, password_hash: str, role: UserRoleEnum) -> UserModel | None:
        user_model = UserModel(name=name, email=email, password_hash=password_hash, role=role)
        self._async_session.add(user_model)

        try:
            await self._async_session.flush()
            return user_model
        except IntegrityError:
            await self._async_session.rollback()
            raise
