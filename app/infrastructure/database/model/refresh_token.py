from uuid import UUID, uuid4
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime, Uuid, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.model.user import UserModel


class RefreshTokenModel(Base):
    """Модель refresh токена в бд"""

    __tablename__ = 'refresh_tokens'

    refresh_token_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey('users.user_id', ondelete='cascade'), nullable=False, index=True)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    expired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    audience: Mapped[str] = mapped_column(String(256), nullable=False, index=True)

    user: Mapped['UserModel'] = relationship('UserModel', back_populates='refresh_tokens', uselist=False, lazy='selectin')
