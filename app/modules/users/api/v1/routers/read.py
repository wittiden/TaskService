from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import Response

from app.common.limiter.config import limiter
from app.common.security.jwt_current import CurrentAdmin, CurrentUser
from app.infrastructure.unit_of_work.uow import UnitOfWork
from app.modules.users.contracts.dtos import FullUserInfoDTO, SecurityUserInfoDTO
from app.modules.users.service.use_cases import ShowUserCase

read_users_router = APIRouter(prefix='/api/v1/users', tags=['users'])
read_admin_users_router = APIRouter(prefix='/api/v1/admin/users', tags=['admin-users'])


@read_admin_users_router.get('/', response_model=list[FullUserInfoDTO], summary='Show users')
@limiter.limit('30/minute')
@inject
async def show_users_endpoint(
    request: Request,
    response: Response,
    current_user: CurrentAdmin,
    case: FromDishka[ShowUserCase],
    uow: FromDishka[UnitOfWork],
    offset: int = 0,
    limit: int = 100,
) -> list[FullUserInfoDTO]:
    return await case.show_users(offset, limit)


@read_users_router.get('/me', response_model=SecurityUserInfoDTO, summary='Show me')
@inject
async def show_me_endpoint(
    current_user: CurrentUser,
    case: FromDishka[ShowUserCase],
    uow: FromDishka[UnitOfWork],
) -> SecurityUserInfoDTO:
    return await case.show_me(current_user)


@read_admin_users_router.get(
    '/{user_id}', response_model=FullUserInfoDTO, summary='Show user by id'
)
@inject
async def show_user_by_id_endpoint(
    current_user: CurrentAdmin,
    user_id: UUID,
    case: FromDishka[ShowUserCase],
    uow: FromDishka[UnitOfWork],
) -> FullUserInfoDTO:
    return await case.show_user_by_id(user_id)
