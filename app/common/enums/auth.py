from enum import StrEnum


class TokenTypeEnum(StrEnum):
    """Енум для перечисления типов токенов"""

    REFRESH_TOKEN = 'refresh_token'
    ACCESS_TOKEN = 'access_token'
