from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.model.task import TaskModel


class TaskAuditModel(Base):
    """Модель аудита задач в бд"""

    __tablename__ = 'task_audits'

    task_audit_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    task_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey('tasks.task_id', ondelete='cascade'), nullable=False, index=True)
    field_name: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    new_value: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    old_value: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC), index=True)

    task: Mapped['TaskModel'] = relationship('TaskModel', back_populates='task_audits', uselist=False, lazy='joined')
