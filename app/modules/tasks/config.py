from pydantic_settings import BaseSettings, SettingsConfigDict


class TaskConfig(BaseSettings):
    """Класс для конфигурации задач"""

    STANDARD_TASK_COUNT_LIMIT: int
    VIP_TASK_COUNT_LIMIT: int

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='UTF-8',
        extra='ignore',
    )
