from pydantic_settings import BaseSettings, SettingsConfigDict


class TaskConfig(BaseSettings):
    """Класс для конфигурации задач"""

    STANDARD_TASK_COUNT_LIMIT: int = 20
    VIP_TASK_COUNT_LIMIT: int = 100

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='UTF-8',
        extra='ignore',
    )
