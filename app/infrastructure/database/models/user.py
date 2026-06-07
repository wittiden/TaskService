from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import DateTime, Enum, String, Boolean, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.common.emums.users import UserRoleEnum
from app.infrastructure.database.base import Base


class UserModel(Base):
    """Модель пользователя в бд"""

    __tablename__ = 'users'

    user_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4())
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(500), nullable=False)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    role: Mapped[UserRoleEnum] = mapped_column(Enum(UserRoleEnum, name='user_role_enum'), default=UserRoleEnum.UNKNOWN_USER, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
