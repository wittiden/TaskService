from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseSettings):
    """Класс для сборки конфигурации бд"""

    DB_USER: str = 'postgres'
    DB_PASS: str = 'pass'
    DB_HOST: str = 'localhost'
    DB_PORT: int = 5432
    DB_NAME: str = 'task_service_dev'

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='UTF-8',
        extra='ignore',
    )

    @property
    def database_url(self) -> str:
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'


database_config = DatabaseConfig()
