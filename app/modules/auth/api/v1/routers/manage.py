from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, status
from starlette.requests import Request
from starlette.responses import Response

from app.common.limiter.config import limiter
from app.common.security.jwt_current import CurrentUser
from app.infrastructure.unit_of_work.uow import UnitOfWork
from app.modules.auth.contracts.dtos import TokenInfoDTO
from app.modules.auth.contracts.schemas import LoginUserSchema, RefreshSchema
from app.modules.auth.service.use_cases import (
    LoginUserCase,
    LogoutUserCase,
    RefreshUserCase,
)

auth_router = APIRouter(prefix='/api/v1/auth', tags=['auth'])


@auth_router.post('/login', response_model=TokenInfoDTO, summary='Login user')
@limiter.limit('5/minute')
@inject
async def login_user_endpoint(
    request: Request,
    response: Response,
    schema: LoginUserSchema,
    case: FromDishka[LoginUserCase],
    uow: FromDishka[UnitOfWork],
) -> TokenInfoDTO:
    return await case.login_user(schema.email, schema.password)


@auth_router.post('/logout', summary='Logout user device', status_code=status.HTTP_204_NO_CONTENT)
@limiter.shared_limit('10/minute', scope='logout_limit')
@inject
async def logout_user_device_endpoint(
    request: Request,
    response: Response,
    current_user: CurrentUser,
    case: FromDishka[LogoutUserCase],
    uow: FromDishka[UnitOfWork],
) -> None:
    await case.logout_user_device(current_user)


@auth_router.post(
    '/logout-all',
    summary='Logout all user device',
    status_code=status.HTTP_204_NO_CONTENT,
)
@limiter.shared_limit('10/minute', scope='logout_limit')
@inject
async def logout_all_user_device_endpoint(
    request: Request,
    response: Response,
    current_user: CurrentUser,
    case: FromDishka[LogoutUserCase],
    uow: FromDishka[UnitOfWork],
) -> None:
    await case.logout_all_user_devices(current_user)


@auth_router.post('/refresh', response_model=TokenInfoDTO, summary='Refresh')
@limiter.limit('3/minute')
@inject
async def refresh_endpoint(
    request: Request,
    response: Response,
    schema: RefreshSchema,
    case: FromDishka[RefreshUserCase],
    uow: FromDishka[UnitOfWork],
) -> TokenInfoDTO:
    return await case.refresh(schema.refresh_token)
