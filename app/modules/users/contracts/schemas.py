from pydantic import BaseModel, EmailStr, Field


class CreateUserSchema(BaseModel):
    """Схема по созданию пользователя"""

    name: str
    email: EmailStr
    password: str


class UpdateUserSchema(BaseModel):
    """Схема по обновлению пользователя"""

    name: str | None = Field(default=None, examples=[None])
    email: EmailStr | None = Field(default=None, examples=[None])
    password: str | None = Field(default=None, examples=[None])
