from datetime import datetime, UTC
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Uuid, ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.model import UserModel


class UserAuditModel(Base):
    """Модель для аудита пользователей в бд"""

    __tablename__ = 'user_audits'

    user_audit_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey('users.user_id', ondelete='cascade'), nullable=False, index=True)
    field_name: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    new_value: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    old_value: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC), index=True)

    user: Mapped['UserModel'] = relationship('UserModel', back_populates='user_audits', uselist=False, lazy='joined')
