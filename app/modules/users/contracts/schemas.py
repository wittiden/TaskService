from pydantic import BaseModel, EmailStr


class CreateUserSchema(BaseModel):
    """Схема по созданию пользователя"""

    name: str
    email: EmailStr
    password: str
