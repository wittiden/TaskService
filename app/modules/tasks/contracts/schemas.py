from pydantic import BaseModel, Field

from app.common.enums.task import TaskImportantLevelEnum, TaskScheduleEnum


class CreateTaskSchema(BaseModel):
    """Схема по созданию задач"""

    title: str
    description: str | None = Field(examples=[None])
    important_level: TaskImportantLevelEnum = Field(examples=[TaskImportantLevelEnum.TRIVIAL])
    schedule_type: TaskScheduleEnum = Field(examples=[TaskScheduleEnum.DAILY])


class UpdateTaskSchema(BaseModel):
    """Схема по обновлению данных задач"""

    title: str | None = Field(examples=[None])
    description: str | None = Field(examples=[None])
    important_level: TaskImportantLevelEnum | None = Field(examples=[None])
    schedule_type: TaskScheduleEnum | None = Field(examples=[None])
