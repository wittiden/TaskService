from slowapi import Limiter
from slowapi.util import get_remote_address

from app.infrastructure.redis.config import redis_config

limiter = Limiter(
    get_remote_address,
    default_limits=['100/minute'],
    headers_enabled=True,
    storage_uri=redis_config.redis_rate_limit_db_url,
    in_memory_fallback_enabled=True,
    in_memory_fallback=['100/minute']
)
