from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, status
from starlette.requests import Request
from starlette.responses import Response

from app.common.limiter.config import limiter
from app.common.security.jwt_current import CurrentAdmin, CurrentUser
from app.infrastructure.unit_of_work.uow import UnitOfWork
from app.modules.users.contracts.dtos import FullUserInfoDTO, SecurityUserInfoDTO
from app.modules.users.contracts.schemas import UpdateUserSchema
from app.modules.users.service.use_cases import DeleteUserCase, ManageUserCase, UpdateUserCase

update_users_router = APIRouter(prefix='/api/v1/users', tags=['users'])
update_admin_users_router = APIRouter(prefix='/api/v1/admin/users', tags=['admin-users'])


@update_users_router.patch('/me', response_model=SecurityUserInfoDTO, summary='Update me')
@limiter.limit('10/minute')
@inject
async def update_me_endpoint(
    request: Request,
    response: Response,
    current_user: CurrentUser,
    schema: UpdateUserSchema,
    case: FromDishka[UpdateUserCase],
    uow: FromDishka[UnitOfWork],
) -> SecurityUserInfoDTO:
    return await case.update_user_params(current_user, schema.model_dump(exclude_none=True))


@update_users_router.patch(
    '/me/close', summary='Close my account', status_code=status.HTTP_204_NO_CONTENT
)
@limiter.limit('5/minute')
@inject
async def close_my_account_endpoint(
    request: Request,
    response: Response,
    current_user: CurrentUser,
    case: FromDishka[DeleteUserCase],
    uow: FromDishka[UnitOfWork],
) -> None:
    await case.close_my_account(current_user)


@update_admin_users_router.patch(
    '/block/{user_id}', response_model=FullUserInfoDTO, summary='Block user account'
)
@limiter.shared_limit('10/minute', scope='block_limit')
@inject
async def block_user_account_endpoint(
    request: Request,
    response: Response,
    current_user: CurrentAdmin,
    user_id: UUID,
    case: FromDishka[ManageUserCase],
    uow: FromDishka[UnitOfWork],
) -> FullUserInfoDTO:
    return await case.block_user(user_id)


@update_admin_users_router.patch(
    '/unblock/{user_id}', response_model=FullUserInfoDTO, summary='Unblock user account'
)
@limiter.shared_limit('10/minute', scope='block_limit')
@inject
async def unblock_user_account_endpoint(
    request: Request,
    response: Response,
    current_user: CurrentAdmin,
    user_id: UUID,
    case: FromDishka[ManageUserCase],
    uow: FromDishka[UnitOfWork],
) -> FullUserInfoDTO:
    return await case.unblock_user(user_id)
