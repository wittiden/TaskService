from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import delete, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.model import RefreshTokenModel


class SessionCommandsRepository:
    """Репозиторий для insert, alter, delete запросов"""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

    async def delete_deactivate_refresh_token_by_id(self, refresh_token_id: UUID) -> UUID | None:
        deleted_obj_id = await self._async_session.execute(
            delete(RefreshTokenModel)
            .where(
                RefreshTokenModel.refresh_token_id == refresh_token_id,
                or_(
                    RefreshTokenModel.revoked_at.is_not(None),
                    RefreshTokenModel.expired_at < datetime.now(UTC),
                ),
            )
            .returning(RefreshTokenModel.refresh_token_id)
        )

        return deleted_obj_id.scalar_one_or_none()

    async def delete_dead_tokens(self) -> int:
        result = await self._async_session.execute(
            delete(RefreshTokenModel)
            .where(
                or_(
                    RefreshTokenModel.revoked_at.is_not(None),
                    RefreshTokenModel.expired_at < datetime.now(UTC),
                )
            )
            .returning(RefreshTokenModel.refresh_token_id)
        )

        deleted_count = len(result.scalars().all())

        await self._async_session.commit()

        return deleted_count
