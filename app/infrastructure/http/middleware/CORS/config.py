from pydantic_settings import BaseSettings, SettingsConfigDict


class CORSConfig(BaseSettings):
    """Класс конфигурации cors для контроля доступа"""

    ALLOW_ORIGINS: str
    ALLOW_METHODS: str
    ALLOW_HEADERS: str
    ALLOW_CREDENTIALS: bool

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='UTF-8',
        extra='ignore',
    )

    @property
    def allow_origins(self) -> list[str]:
        return self.ALLOW_ORIGINS.split(',')

    @property
    def allow_methods(self) -> list[str]:
        return self.ALLOW_METHODS.split(',')

    @property
    def allow_headers(self) -> list[str]:
        return self.ALLOW_HEADERS.split(',')


cors_config = CORSConfig()
