from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, status
from starlette.requests import Request
from starlette.responses import Response

from app.common.limiter.config import limiter
from app.common.security.jwt_current import CurrentAdmin
from app.infrastructure.unit_of_work.uow import UnitOfWork
from app.modules.users.service.use_cases import DeleteUserCase

delete_admin_users_router = APIRouter(prefix='/api/v1/admin/users', tags=['admin-users'])


@delete_admin_users_router.delete(
    '/{user_id}', summary='Delete user account', status_code=status.HTTP_204_NO_CONTENT
)
@limiter.limit('10/minute')
@inject
async def delete_user_account_endpoint(
    request: Request,
    response: Response,
    current_user: CurrentAdmin,
    user_id: UUID,
    case: FromDishka[DeleteUserCase],
    uow: FromDishka[UnitOfWork],
) -> None:
    await case.delete_user_account(user_id)
