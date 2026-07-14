from datetime import datetime
from uuid import UUID

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.model import RefreshTokenModel
from app.infrastructure.database.model.user import UserModel


class AuthQueriesRepository:
    """Репозиторий для select запросов"""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

    async def select_user_id_pass_role_by_email(self, email: str) -> dict | None:
        columns = await self._async_session.execute(
            select(
                UserModel.user_id,
                UserModel.password_hash,
                UserModel.role,
                UserModel.blocked_at,
                UserModel.closed_at,
            ).where(UserModel.email == email)
        )
        columns = columns.mappings().one_or_none()
        return dict(columns) if columns else None

    async def select_user_by_id(self, user_id: UUID) -> UserModel | None:
        user = await self._async_session.get(UserModel, user_id)
        return user

    async def select_user_role_by_id(self, user_id: UUID) -> dict | None:
        columns = await self._async_session.execute(
            select(
                UserModel.user_id,
                UserModel.role,
                UserModel.blocked_at,
                UserModel.closed_at,
            ).where(UserModel.user_id == user_id)
        )
        columns = columns.mappings().one_or_none()
        return dict(columns) if columns else None

    async def select_refresh_token_revoked_by_id(self, refresh_token_id: UUID) -> datetime | None:
        obj = await self._async_session.execute(
            select(RefreshTokenModel.revoked_at).where(
                RefreshTokenModel.refresh_token_id == refresh_token_id
            )
        )
        return obj.scalar_one_or_none()

    async def select_not_revoked_tokens_by_user_id(self, user_id: UUID) -> bool | None:
        result = await self._async_session.execute(
            select(
                exists().where(
                    RefreshTokenModel.user_id == user_id,
                    RefreshTokenModel.revoked_at.is_(None),
                )
            )
        )

        return result.scalar()
