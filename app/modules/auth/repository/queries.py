from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.model.user import UserModel


class AuthQueriesRepository:
    """Репозиторий для select запросов"""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

    async def select_user_id_pass_role_by_email(self, email: str) -> dict | None:
        columns = await self._async_session.execute(select(UserModel.user_id, UserModel.password_hash, UserModel.role, UserModel.blocked_at, UserModel.closed_at).where(UserModel.email == email))
        columns = columns.mappings().one_or_none()
        return dict(columns) if columns else None

    async def select_user_by_id(self, user_id: UUID) -> UserModel | None:
        user = await self._async_session.get(UserModel, user_id)
        return user
