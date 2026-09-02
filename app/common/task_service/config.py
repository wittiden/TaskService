from pydantic_settings import BaseSettings, SettingsConfigDict


class TaskServiceConfig(BaseSettings):
    """Класс для конфигурации сервиса задач"""

    RABBITMQ_USER: str = 'user'
    RABBITMQ_PASSWORD: str = ''
    RABBITMQ_HOST: str = 'localhost'
    RABBITMQ_PORT: int = 5672

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='UTF-8', extra='ignore')


task_service_config = TaskServiceConfig()
