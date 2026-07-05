from datetime import datetime, UTC
from typing import Any, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import String, ForeignKey, DateTime, Uuid, JSON, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.enums.user import UserRoleEnum
from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.model.refresh_token import RefreshTokenModel


class UserModel(Base):
    """Модель пользователя в бд"""

    __tablename__ = 'users'

    user_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(256), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(500), nullable=False)
    role: Mapped[UserRoleEnum] = mapped_column(Enum(UserRoleEnum,name='user_role_enum'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, onupdate=lambda: datetime.now(UTC))
    blocked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user_audits: Mapped[list[UserAuditModel]] = relationship('UserAuditModel', back_populates='user', uselist=True, lazy='selectin', cascade='all, delete-orphan')
    refresh_tokens: Mapped[list['RefreshTokenModel']] = relationship('RefreshTokenModel', back_populates='user', uselist=True, lazy='selectin', cascade='all, delete-orphan')


class UserAuditModel(Base):
    """Модель для аудита пользователей в бд"""

    __tablename__ = 'user_audits'

    user_audits_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey('users.user_id', ondelete='cascade'), nullable=False)
    field_name: Mapped[str] = mapped_column(String(256), nullable=False)
    new_value: Mapped[Any] = mapped_column(JSON, nullable=False)
    old_value: Mapped[Any | None] = mapped_column(JSON, nullable=True)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))

    user: Mapped[UserModel] = relationship('UserModel', back_populates='user_audits', uselist=False, lazy='selectin')
