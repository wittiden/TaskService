from datetime import datetime, UTC
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import update, delete

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

    async def alter_user_closed_param(self, user_id: UUID) -> datetime | None:
        result = await self._async_session.execute(update(UserModel)
                                          .where(UserModel.user_id == user_id, UserModel.closed_at.is_(None))
                                          .values(closed_at=datetime.now(UTC))
                                          .returning(UserModel.closed_at))

        return result.scalar_one_or_none()

    async def delete_closed_user_by_id(self, user_id: UUID) -> UUID | None:
        deleted_obj_id = await self._async_session.execute(delete(UserModel)
                                          .where(UserModel.user_id == user_id, UserModel.closed_at.is_not(None))
                                          .returning(UserModel.user_id))

        deleted_obj_id = deleted_obj_id.scalar_one_or_none()
        return deleted_obj_id

    async def alter_block_user_by_id(self, user_id: UUID) -> UserModel | None:
        user = await self._async_session.execute(update(UserModel)
                                          .where(UserModel.user_id == user_id, UserModel.blocked_at.is_(None))
                                          .values(blocked_at=datetime.now(UTC))
                                          .returning(UserModel))

        return user.scalar_one_or_none()

    async def alter_unblock_user_by_id(self, user_id: UUID) -> UserModel | None:
        user = await self._async_session.execute(update(UserModel)
                                                 .where(UserModel.user_id == user_id, UserModel.blocked_at.is_not(None))
                                                 .values(blocked_at=None)
                                                 .returning(UserModel))

        return user.scalar_one_or_none()

    async def alter_user_params(self, user_id: UUID, new_params: dict) -> UserModel | None:
        try:
            user = await self._async_session.execute(update(UserModel)
                                                     .where(UserModel.user_id == user_id)
                                                     .values(**new_params)
                                                     .returning(UserModel))

            return user.scalar_one_or_none()

        except IntegrityError:
            await self._async_session.rollback()
            raise
