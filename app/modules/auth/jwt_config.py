from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class TokenConfig(BaseSettings):
    """Класс для конфигурации токенов"""

    ACCESS_TOKEN_ALGORITHM: str = 'RS256'
    ACCESS_TOKEN_PRIVATE_KEY_PATH: str = 'certs/access-private'
    ACCESS_TOKEN_PUBLIC_KEY_PATH: str = 'certs/access-public'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 5
    ACCESS_TOKEN_AUDIENCE: str = 'access-api'

    REFRESH_TOKEN_ALGORITHM: str = 'RS256'
    REFRESH_TOKEN_PRIVATE_KEY_PATH: str = 'certs/refresh-private'
    REFRESH_TOKEN_PUBLIC_KEY_PATH: str = 'certs/refresh-public'
    REFRESH_TOKEN_EXPIRE_DAYS: int = 1
    REFRESH_TOKEN_AUDIENCE: str = 'refresh-api'
    REFRESH_TOKEN_VERSION: int = 1

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='UTF-8',
        extra='ignore',
    )

    @property
    def access_token_private_key(self) -> str:
        return Path(self.ACCESS_TOKEN_PRIVATE_KEY_PATH).read_text()

    @property
    def access_token_public_key(self) -> str:
        return Path(self.ACCESS_TOKEN_PUBLIC_KEY_PATH).read_text()

    @property
    def refresh_token_private_key(self) -> str:
        return Path(self.REFRESH_TOKEN_PRIVATE_KEY_PATH).read_text()

    @property
    def refresh_token_public_key(self) -> str:
        return Path(self.REFRESH_TOKEN_PUBLIC_KEY_PATH).read_text()
