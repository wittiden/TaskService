from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import DateTime, Enum, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.common.enums.users import UserRoleEnum
from app.infrastructure.database.base import Base


class UserModel(Base):
    """Модель пользователя в бд"""

    __tablename__ = 'users'

    user_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(500), nullable=False)
    role: Mapped[UserRoleEnum] = mapped_column(Enum(UserRoleEnum, name='user_role_enum'), default=UserRoleEnum.UNKNOWN_USER, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    blocked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)

    def __repr__(self) -> str:
        return (
                f'user_id: {self.user_id}, '
                f'name: {self.name}, '
                f'email: {self.email}, '
                f'role: {self.role}, '
                f'created_at: {self.created_at}, '
                f'closed_at: {self.closed_at}, '
                f'updated_at: {self.updated_at}, '
                f'blocked_at: {self.blocked_at}, '
                )
