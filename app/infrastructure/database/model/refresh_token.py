from uuid import UUID, uuid4
from datetime import datetime

from sqlalchemy import Integer, String, DateTime, Uuid, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base
from app.infrastructure.database.model.user import UserModel


class RefreshTokenModel(Base):
    """Модель refresh токена в бд"""

    __tablename__ = 'refresh_tokens'

    refresh_token_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey('users.user_id', ondelete='cascade'), nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    audience: Mapped[str] = mapped_column(String(256), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)

    user: Mapped[UserModel] = relationship('UserModel', back_populates='refresh_tokens', uselist=False, lazy='selectin')
