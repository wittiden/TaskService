from uuid import UUID
from sqlalchemy import Uuid, String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.infrastructure.database.base import Base


class RefreshTokenModel(Base):
    """Модель refresh jwt токена в бд"""

    __tablename__ = 'refresh_tokens'

    refresh_token_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey('users.user_id'), nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    audience: Mapped[str] = mapped_column(String(24), nullable=False)
