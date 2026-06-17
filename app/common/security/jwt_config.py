from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class JWTConfig(BaseSettings):
    """Конфигурация для jwt токенов"""

    ACCESS_TOKEN_ALGORITHM: str
    ACCESS_TOKEN_PUBLIC_KEY_PATH: Path
    ACCESS_TOKEN_PRIVATE_KEY_PATH: Path
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ACCESS_TOKEN_AUDIENCE: str

    REFRESH_TOKEN_ALGORITHM: str
    REFRESH_TOKEN_PUBLIC_KEY_PATH: Path
    REFRESH_TOKEN_PRIVATE_KEY_PATH: Path
    REFRESH_TOKEN_EXPIRE_DAYS: int
    REFRESH_TOKEN_VERSION: int
    REFRESH_TOKEN_AUDIENCE: str
    REFRESH_TOKEN_RETENTION_DAYS: int

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='UTF-8', extra='ignore')

    @property
    def access_token_public_key(self) -> str:
        return self.ACCESS_TOKEN_PUBLIC_KEY_PATH.read_text()

    @property
    def access_token_private_key(self) -> str:
        return self.ACCESS_TOKEN_PRIVATE_KEY_PATH.read_text()

    @property
    def refresh_token_public_key(self) -> str:
        return self.REFRESH_TOKEN_PUBLIC_KEY_PATH.read_text()

    @property
    def refresh_token_private_key(self) -> str:
        return self.REFRESH_TOKEN_PRIVATE_KEY_PATH.read_text()
