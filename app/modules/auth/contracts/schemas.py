from pydantic import BaseModel, EmailStr


class LoginUserSchema(BaseModel):
    """Схема для входа в аккаунт пользователя"""

    email: EmailStr
    password: str


class RefreshSchema(BaseModel):
    """Схема для обновления токена"""

    refresh_token: str
