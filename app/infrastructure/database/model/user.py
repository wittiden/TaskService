from datetime import datetime, UTC
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, Uuid, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.enums.user import UserRoleEnum
from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.model.refresh_token import RefreshTokenModel
    from user_audit import UserAuditModel
    from task import TaskModel


class UserModel(Base):
    """Модель пользователя в бд"""

    __tablename__ = 'users'

    user_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(256), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(500), nullable=False)
    role: Mapped[UserRoleEnum] = mapped_column(Enum(UserRoleEnum,name='user_role_enum'), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC), index=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, onupdate=lambda: datetime.now(UTC))
    blocked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user_audits: Mapped[list[UserAuditModel]] = relationship('UserAuditModel', back_populates='user', uselist=True, lazy='selectin', cascade='all, delete-orphan')
    refresh_tokens: Mapped[list['RefreshTokenModel']] = relationship('RefreshTokenModel', back_populates='user', uselist=True, lazy='selectin', cascade='all, delete-orphan')
    tasks: Mapped[list['TaskModel']] = relationship('TaskModel', back_populates='user', uselist=True, lazy='selectin', cascade='all, delete-orphan')
