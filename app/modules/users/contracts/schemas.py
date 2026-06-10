from pydantic import BaseModel, EmailStr, Field


class CreateUserSchema(BaseModel):
    """Схема по созданию пользователя"""

    name: str
    email: EmailStr
    password: str


class UpdateUserSchema(BaseModel):
    """Схема по обновлению данных пользователя"""

    name: str | None = Field(default=None)
    email: EmailStr | None = Field(default=None)
    password: str | None = Field(default=None)
