from fastapi import APIRouter
from dishka.integrations.fastapi import FromDishka, inject

from app.modules.auth.contracts.dtos import TokenInfoDTO
from app.modules.auth.contracts.schemas import LoginUserSchema
from app.modules.auth.service.use_cases import LoginUserCase

auth_router = APIRouter(prefix='/api/v1/auth', tags=['auth'])


@auth_router.post('/login', response_model=TokenInfoDTO, summary='Login user')
@inject
async def login_user_endpoint(schema: LoginUserSchema, case: FromDishka[LoginUserCase]) -> TokenInfoDTO:
    return await case.login_user(schema.email, schema.password)
