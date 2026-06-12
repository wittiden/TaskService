from uuid import UUID
from sqlalchemy import Uuid, String, DateTime, ForeignKey, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.infrastructure.database.base import Base


class RefreshTokenModel(Base):
    """Модель refresh jwt токена в бд"""

    __tablename__ = 'refresh_tokens'

    refresh_token_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey('users.user_id'), nullable=False, index=True)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    version: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    audience: Mapped[str] = mapped_column(String(24), nullable=False)

    def __repr__(self) -> str:
        return (
                f'jti: {self.refresh_token_id},'
                f' sub: {self.user_id},'
                f' iat: {self.issued_at},'
                f' exp: {self.expires_at},'
                f' revoked_at: {self.revoked_at},'
                f' version: {self.version},'
                f' aud: {self.audience}'
        )
