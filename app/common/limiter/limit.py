from slowapi import Limiter
from slowapi.util import get_remote_address


limiter = Limiter(
    key_func=get_remote_address,
    headers_enabled=True,
    default_limits=['100/minute'],
    # storage_uri=,
    # in_memory_fallback_enabled=True,
    # in_memory_fallback=['100/minute'],
)
