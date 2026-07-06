from fastapi import APIRouter
from dishka.integrations.fastapi import FromDishka, inject

from app.common.security.jwt_current import CurrentStandard, CurrentAdmin, CurrentVip
from app.modules.auth.contracts.dtos import TokenInfoDTO
from app.modules.auth.contracts.schemas import LoginUserSchema, RefreshSchema
from app.modules.auth.service.use_cases import LoginUserCase, LogoutUserCase, RefreshUserCase

auth_router = APIRouter(prefix='/api/v1/auth', tags=['auth'])


@auth_router.post('/login', response_model=TokenInfoDTO, summary='Login user')
@inject
async def login_user_endpoint(schema: LoginUserSchema, case: FromDishka[LoginUserCase]) -> TokenInfoDTO:
    return await case.login_user(schema.email, schema.password)


@auth_router.post('/logout', summary='Logout user device')
@inject
async def logout_user_device_endpoint(current_user: CurrentStandard | CurrentAdmin | CurrentVip, case: FromDishka[LogoutUserCase]) -> None:
    return await case.logout_user_device(current_user)


@auth_router.post('/logout', summary='Logout all user device')
@inject
async def logout_all_user_device_endpoint(current_user: CurrentStandard | CurrentAdmin | CurrentVip, case: FromDishka[LogoutUserCase]) -> None:
    return await case.logout_all_user_devices(current_user)


@auth_router.post('/refresh', response_model=TokenInfoDTO, summary='Refresh')
@inject
async def refresh_endpoint(schema: RefreshSchema, case: FromDishka[RefreshUserCase]) -> TokenInfoDTO:
    return await case.refresh(schema.refresh_token)
