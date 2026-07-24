from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.common.enums.task import TaskImportantLevelEnum, TaskScheduleEnum


class FullTaskInfoDTO(BaseModel):
    """DTO для передачи полных данных о задаче"""

    task_id: UUID
    user_id: UUID
    created_at: datetime
    closed_at: datetime | None
    completed_at: datetime | None
    updated_at: datetime | None
    important_level: TaskImportantLevelEnum
    schedule_type: TaskScheduleEnum
    title: str
    description: str | None

    model_config = ConfigDict(
        from_attributes=True,
    )


class SecurityTaskInfoDTO(BaseModel):
    """DTO для передачи безопасных данных о задаче"""

    task_id: UUID
    created_at: datetime
    closed_at: datetime | None
    completed_at: datetime | None
    important_level: TaskImportantLevelEnum
    schedule_type: TaskScheduleEnum
    title: str
    description: str | None

    model_config = ConfigDict(
        from_attributes=True,
    )
