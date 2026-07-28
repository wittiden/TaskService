from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, status
from starlette.requests import Request
from starlette.responses import Response

from app.common.limiter.config import limiter
from app.common.security.jwt_current import CurrentAdmin
from app.infrastructure.unit_of_work.uow import UnitOfWork
from app.modules.sessions.service.use_cases import DeleteRefreshTokenCase

delete_admin_sessions_router = APIRouter(prefix='/api/v1/admin/sessions', tags=['admin-sessions'])


@delete_admin_sessions_router.delete(
    '/{refresh_token_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Delete refresh token by id',
)
@limiter.limit('20/minute')
@inject
async def delete_refresh_token_by_id_endpoint(
    response: Response,
    request: Request,
    current_user: CurrentAdmin,
    refresh_token_id: UUID,
    case: FromDishka[DeleteRefreshTokenCase],
    uow: FromDishka[UnitOfWork],
) -> None:
    return await case.delete_refresh_token_by_id(refresh_token_id)
