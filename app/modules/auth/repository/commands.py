from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.model.refresh_token import RefreshTokenModel


class AuthCommandsRepository:
    """Репозиторий для insert, alter, delete команд"""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

    async def insert_refresh_token_data(self, refresh_token_id: UUID, user_id: UUID, issued_at: datetime, expired_at: datetime, audience: str) -> RefreshTokenModel:
        refresh_token_model = RefreshTokenModel(refresh_token_id=refresh_token_id, user_id=user_id, issued_at=issued_at, expired_at=expired_at, audience=audience)
        self._async_session.add(refresh_token_model)

        await self._async_session.flush()
        return refresh_token_model

    async def alter_user_refresh_tokens_revoked_param(self, user_id: UUID, audience: str) -> None:
        await self._async_session.execute(
            update(RefreshTokenModel)
            .where(RefreshTokenModel.user_id == user_id, RefreshTokenModel.audience == audience, RefreshTokenModel.revoked_at.is_(None))
            .values(revoked_at=datetime.now(UTC))
        )

    async def alter_all_user_refresh_tokens_revoked_param(self, user_id: UUID) -> None:
        await self._async_session.execute(
            update(RefreshTokenModel).where(RefreshTokenModel.user_id == user_id, RefreshTokenModel.revoked_at.is_(None)).values(revoked_at=datetime.now(UTC))
        )

    async def alter_refresh_token_revoked_param(self, refresh_token_id: UUID) -> None:
        await self._async_session.execute(
            update(RefreshTokenModel).where(RefreshTokenModel.refresh_token_id == refresh_token_id, RefreshTokenModel.revoked_at.is_(None)).values(revoked_at=datetime.now(UTC))
        )
