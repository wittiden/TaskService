from fastapi import APIRouter
from dishka.integrations.fastapi import FromDishka, inject
from starlette.requests import Request
from starlette.responses import Response

from app.common.limiter.config import limiter
from app.common.security.jwt_current import CurrentUser
from app.modules.auth.contracts.dtos import TokenInfoDTO
from app.modules.auth.contracts.schemas import LoginUserSchema, RefreshSchema
from app.modules.auth.service.use_cases import LoginUserCase, LogoutUserCase, RefreshUserCase

auth_router = APIRouter(prefix='/api/v1/auth', tags=['auth'])


@limiter.limit('5/minute')
@auth_router.post('/login', response_model=TokenInfoDTO, summary='Login user')
@inject
async def login_user_endpoint(request: Request, response: Response, schema: LoginUserSchema, case: FromDishka[LoginUserCase]) -> TokenInfoDTO:
    return await case.login_user(schema.email, schema.password)


@limiter.shared_limit('10/minute', scope='logout_limit')
@auth_router.post('/logout', summary='Logout user device')
@inject
async def logout_user_device_endpoint(request: Request, response: Response, current_user: CurrentUser, case: FromDishka[LogoutUserCase]) -> None:
    return await case.logout_user_device(current_user)


@limiter.shared_limit('10/minute', scope='logout_limit')
@auth_router.post('/logout-all', summary='Logout all user device')
@inject
async def logout_all_user_device_endpoint(request: Request, response: Response, current_user: CurrentUser, case: FromDishka[LogoutUserCase]) -> None:
    return await case.logout_all_user_devices(current_user)


@limiter.limit('3/minute')
@auth_router.post('/refresh', response_model=TokenInfoDTO, summary='Refresh')
@inject
async def refresh_endpoint(request: Request, response: Response, schema: RefreshSchema, case: FromDishka[RefreshUserCase]) -> TokenInfoDTO:
    return await case.refresh(schema.refresh_token)
