from uuid import UUID

from fastapi import APIRouter, status
from starlette.responses import Response
from starlette.requests import Request
from dishka.integrations.fastapi import inject, FromDishka

from app.common.limiter.config import limiter
from app.infrastructure.unit_of_work.uow import UnitOfWork
from app.modules.sessions.contracts.dtos import FullRefreshTokenInfoDTO
from app.modules.sessions.service.use_cases import ShowRefreshTokenCase, DeleteRefreshTokenCase
from app.common.security.jwt_current import CurrentAdmin

admin_tokens_router = APIRouter(prefix='/api/v1/admin/tokens', tags=['admin-tokens'])


@admin_tokens_router.get('/', response_model=list[FullRefreshTokenInfoDTO], summary='Show refresh tokens')
@limiter.limit('30/minute')
@inject
async def show_refresh_tokens_endpoint(response: Response, request: Request, current_user: CurrentAdmin, case: FromDishka[ShowRefreshTokenCase], uow: FromDishka[UnitOfWork], offset: int = 0, limit: int = 100) -> list[FullRefreshTokenInfoDTO]:
    return await case.show_refresh_tokens(offset, limit)


@admin_tokens_router.get('/{user_id}', response_model=list[FullRefreshTokenInfoDTO], summary='Show user active refresh tokens')
@limiter.limit('30/minute')
@inject
async def show_user_active_refresh_tokens_endpoint(response: Response, request: Request, current_user: CurrentAdmin, user_id: UUID, case: FromDishka[ShowRefreshTokenCase], uow: FromDishka[UnitOfWork], offset: int = 0, limit: int = 100) -> list[FullRefreshTokenInfoDTO]:
    return await case.show_user_active_refresh_tokens(user_id, offset, limit)


@admin_tokens_router.get('/by-id/{refresh_token_id}', response_model=FullRefreshTokenInfoDTO, summary='Show refresh token by id')
@inject
async def show_refresh_token_by_id_endpoint(current_user: CurrentAdmin, refresh_token_id: UUID, case: FromDishka[ShowRefreshTokenCase], uow: FromDishka[UnitOfWork]) -> FullRefreshTokenInfoDTO:
    return await case.show_refresh_token_by_id(refresh_token_id)


@admin_tokens_router.delete('/{refresh_token_id}', status_code=status.HTTP_204_NO_CONTENT, summary='Delete refresh token by id')
@limiter.limit('20/minute')
@inject
async def delete_refresh_token_by_id_endpoint(response: Response, request: Request, current_user: CurrentAdmin, refresh_token_id: UUID, case: FromDishka[DeleteRefreshTokenCase], uow: FromDishka[UnitOfWork]) -> None:
    return await case.delete_refresh_token_by_id(refresh_token_id)
