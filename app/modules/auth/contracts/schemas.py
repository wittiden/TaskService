from pydantic import BaseModel, EmailStr


class LoginUserSchema(BaseModel):
    """Схема для входа в аккаунт"""

    email: EmailStr
    password: str


class RefreshSchema(BaseModel):
    """Схема для обновления токенов"""

    refresh_token: str
