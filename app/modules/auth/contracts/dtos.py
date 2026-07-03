from pydantic import BaseModel


class TokenInfoDTO(BaseModel):
    """DTO для передачи данных токенов"""

    access_token: str
    refresh_token: str
    token_type: str = 'Bearer'