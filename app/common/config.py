from pydantic_settings import BaseSettings, SettingsConfigDict


class ApplicationConfig(BaseSettings):
    """Класс для получения общих env программы"""

    ENVIRONMENT: str = 'dev'

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='UTF-8',
        extra='ignore',
    )

    @property
    def is_dev(self) -> bool:
        return self.ENVIRONMENT == 'dev'

    @property
    def is_test(self) -> bool:
        return self.ENVIRONMENT == 'test'

    @property
    def is_prod(self) -> bool:
        return self.ENVIRONMENT == 'prod'


application_config = ApplicationConfig()
