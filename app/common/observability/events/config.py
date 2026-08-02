from pydantic_settings import BaseSettings, SettingsConfigDict


class EventsConfig(BaseSettings):
    """Класс для конфигурации событий"""

    SENTRY_DSN: str = 'dsn'

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='UTF-8',
        extra='ignore',
    )


event_config = EventsConfig()
