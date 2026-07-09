from datetime import datetime, UTC
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import update

from app.common.enums.user import UserRoleEnum
from app.infrastructure.database.model.user import UserModel


class UserCommandsRepository:
    """Репозиторий для insert, alter, delete запросов"""

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

    async def alter_user_closed_param(self, user_id: UUID) -> None:
        await self._async_session.execute(update(UserModel)
                                          .where(UserModel.user_id == user_id, UserModel.closed_at.is_(None))
                                          .values(closed_at=datetime.now(UTC)))
