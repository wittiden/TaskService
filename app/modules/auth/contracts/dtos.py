from pydantic import BaseModel, ConfigDict


class TokenInfoDTO(BaseModel):
    """DTO для передачи данных токенов"""

    access_token: str
    refresh_token: str
    token_type: str = 'Bearer'

    model_config = ConfigDict(
        from_attributes=True,
    )
