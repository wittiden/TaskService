from pydantic_settings import BaseSettings, SettingsConfigDict


class UserGuardConfig(BaseSettings):
    """Конфигурация бизнес правил пользователя"""

    ACCOUNT_DELETION_GRACE_DAYS: int

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='UTF-8', extra='ignore')
