from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import Response

from app.common.limiter.config import limiter
from app.common.security.jwt_current import CurrentAdmin
from app.infrastructure.unit_of_work.uow import UnitOfWork
from app.modules.sessions.contracts.dtos import FullRefreshTokenInfoDTO
from app.modules.sessions.service.use_cases import ShowRefreshTokenCase

read_admin_sessions_router = APIRouter(prefix='/api/v1/admin/sessions', tags=['admin-sessions'])


@read_admin_sessions_router.get(
    '/', response_model=list[FullRefreshTokenInfoDTO], summary='Show refresh tokens'
)
@limiter.limit('30/minute')
@inject
async def show_refresh_tokens_endpoint(
    response: Response,
    request: Request,
    current_user: CurrentAdmin,
    case: FromDishka[ShowRefreshTokenCase],
    uow: FromDishka[UnitOfWork],
    offset: int = 0,
    limit: int = 100,
) -> list[FullRefreshTokenInfoDTO]:
    return await case.show_refresh_tokens(offset, limit)


@read_admin_sessions_router.get(
    '/by-id/{refresh_token_id}',
    response_model=FullRefreshTokenInfoDTO,
    summary='Show refresh token by id',
)
@inject
async def show_refresh_token_by_id_endpoint(
    current_user: CurrentAdmin,
    refresh_token_id: UUID,
    case: FromDishka[ShowRefreshTokenCase],
    uow: FromDishka[UnitOfWork],
) -> FullRefreshTokenInfoDTO:
    return await case.show_refresh_token_by_id(refresh_token_id)


@read_admin_sessions_router.get(
    '/{user_id}',
    response_model=list[FullRefreshTokenInfoDTO],
    summary='Show user active refresh tokens',
)
@limiter.limit('30/minute')
@inject
async def show_user_active_refresh_tokens_endpoint(
    response: Response,
    request: Request,
    current_user: CurrentAdmin,
    user_id: UUID,
    case: FromDishka[ShowRefreshTokenCase],
    uow: FromDishka[UnitOfWork],
    offset: int = 0,
    limit: int = 100,
) -> list[FullRefreshTokenInfoDTO]:
    return await case.show_user_active_refresh_tokens(user_id, offset, limit)
