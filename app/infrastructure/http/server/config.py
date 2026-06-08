from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerConfig(BaseSettings):
    """Класс для сборки конфигурации сервера"""

    SERVER_HOST: str
    SERVER_PORT: int
    SERVER_WORKERS: int
    SERVER_WORKER_CLASS: str
    SERVER_RELOAD: bool
    SERVER_TIMEOUT: int
    SERVER_UVICORN_ACCESS_LOG: bool
    SERVER_GUNICORN_ACCESS_LOG: str | None

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='UTF-8', extra='ignore')
