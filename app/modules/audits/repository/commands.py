from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.model import UserAuditModel


class UserAuditCommandsRepository:
    """Репозиторий для insert, alter, delete запросов"""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

    async def insert_user_audit_obj(
        self,
        user_id: UUID,
        field_name: str,
        old_value: str | None,
        new_value: str | None,
    ) -> None:
        user_audit = UserAuditModel(
            user_id=user_id,
            field_name=field_name,
            new_value=new_value,
            old_value=old_value,
        )

        try:
            self._async_session.add(user_audit)
            await self._async_session.flush()

        except IntegrityError:
            await self._async_session.rollback()
            raise
