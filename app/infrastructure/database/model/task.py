from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.enums.task import TaskImportantLevelEnum, TaskScheduleEnum
from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.model import UserModel
    from app.infrastructure.database.model.task_audit import TaskAuditModel


class TaskModel(Base):
    """Модель задачи в бд"""

    __tablename__ = 'tasks'

    task_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey('users.user_id', ondelete='cascade'),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        index=True,
    )
    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, onupdate=lambda: datetime.now(UTC)
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    important_level: Mapped[TaskImportantLevelEnum] = mapped_column(
        Enum(TaskImportantLevelEnum, name='task_important_level_enum'),
        nullable=False,
        index=True,
    )
    schedule_type: Mapped[TaskScheduleEnum] = mapped_column(
        Enum(TaskScheduleEnum, name='task_schedule_enum'), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

    user: Mapped['UserModel'] = relationship(
        'UserModel', back_populates='tasks', uselist=False, lazy='joined'
    )
    task_audits: Mapped[list['TaskAuditModel']] = relationship(
        'TaskAuditModel',
        back_populates='task',
        uselist=True,
        lazy='selectin',
        cascade='all, delete-orphan',
    )

    def __repr__(self) -> str:
        return (
            f'task_id: {self.task_id},'
            f'user_id: {self.user_id},'
            f'created_at: {self.created_at},'
            f'closed_at: {self.closed_at},'
            f'completed_at: {self.completed_at},'
            f'updated_at: {self.updated_at},'
            f'important_level: {self.important_level},'
            f'schedule_type: {self.schedule_type},'
            f'title: {self.title},'
            f'description: {self.description}'
        )
