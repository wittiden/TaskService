from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisConfig(BaseSettings):
    """Класс для конфигурации настроек redis"""

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASS: str
    REDIS_DB: int
    REDIS_RATE_LIMIT_DB: int
    REDIS_QUEUE_DB: int
    REDIS_STATS_DB: int

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='UTF-8', extra='ignore')

    def _redis_url(self, redis_db_type: int) -> str:
        return f'redis://:{self.REDIS_PASS}@{self.REDIS_HOST}:{self.REDIS_PORT}/{redis_db_type}'

    @property
    def redis_db_url(self) -> str:
        return self._redis_url(self.REDIS_DB)

    @property
    def redis_rate_limit_db_url(self) -> str:
        return self._redis_url(self.REDIS_RATE_LIMIT_DB)

    @property
    def redis_queue_db_url(self) -> str:
        return self._redis_url(self.REDIS_QUEUE_DB)

    @property
    def redis_stats_db_url(self) -> str:
        return self._redis_url(self.REDIS_STATS_DB)


redis_config = RedisConfig()
