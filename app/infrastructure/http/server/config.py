from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerConfig(BaseSettings):
    """Класс для сборки конфигурации сервера"""

    SERVER_HOST: str = '0.0.0.0'
    SERVER_PORT: int = 8000
    SERVER_WORKERS: int = 1
    SERVER_WORKER_CLASS: str = 'uvicorn.workers.UvicornWorker'
    SERVER_RELOAD: bool = False
    SERVER_TIMEOUT: int = 30
    SERVER_UVICORN_ACCESS_LOG: bool = False
    SERVER_GUNICORN_ACCESS_LOG: str | None = None

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='UTF-8', extra='ignore')


server_config = ServerConfig()
