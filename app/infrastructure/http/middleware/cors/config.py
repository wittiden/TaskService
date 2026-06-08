from pydantic_settings import BaseSettings, SettingsConfigDict


class CORSConfig(BaseSettings):
    """Класс для конфигурации безопасности через cors в проекте"""

    ALLOW_ORIGINS: str
    ALLOW_METHODS: str
    ALLOW_HEADERS: str

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='UTF-8', extra='ignore')


cors_config = CORSConfig()
