from pydantic_settings import BaseSettings, SettingsConfigDict


class EmailServiceConfig(BaseSettings):
    """Конфигурация сервиса по отправке писем"""

    SMTP_HOST: str = 'smtp.gmail.com'
    SMTP_PORT: int = 587
    SMTP_USER: str = 'email@example.com'
    SMTP_PASS: str = ''

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='UTF-8',
        extra='ignore',
    )


email_service_config = EmailServiceConfig()
