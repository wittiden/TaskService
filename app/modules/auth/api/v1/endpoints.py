from uuid import UUID

from fastapi import APIRouter, Request
from dishka.integrations.fastapi import FromDishka, inject

from app.common.limiter.limit import limiter
from app.common.security.jwt_current import CurrentUser, CurrentAdmin
from app.modules.auth.contracts.dtos import TokensInfoDTO, FullRefreshTokenInfoDTO
from app.modules.auth.contracts.schemas import LoginUserSchema, RefreshSchema
from app.modules.auth.service.use_cases import AuthUserCase, ShowRefreshTokenCase, DeleteRefreshTokenCase

auth_router = APIRouter(prefix='/api/v1/auth', tags=['auth'])
admin_refresh_tokens_router = APIRouter(prefix='/api/v1/admin/refresh-tokens', tags=['admin-refresh-tokens'])


@auth_router.post('/login', response_model=TokensInfoDTO, summary='Login user')
@limiter.limit('5/minute')
@inject
async def login_user_endpoint(request: Request, schema: LoginUserSchema, service: FromDishka[AuthUserCase]) -> TokensInfoDTO:
    return await service.login_user(schema.email, schema.password)


@auth_router.post('/logout', summary='Logout user')
@limiter.limit('10/minute')
@inject
async def logout_user_endpoint(request: Request, current_user: CurrentUser, service: FromDishka[AuthUserCase]) -> None:
    await service.logout(current_user)


@auth_router.post('/refresh', response_model=TokensInfoDTO, summary='Refresh tokens')
@limiter.limit('20/minute')
@inject
async def refresh_tokens_endpoint(request: Request, schema: RefreshSchema, service: FromDishka[AuthUserCase]) -> TokensInfoDTO:
    return await service.refresh(schema.refresh_token)


@admin_refresh_tokens_router.get('/', response_model=list[FullRefreshTokenInfoDTO], summary='Show refresh tokens')
@inject
async def show_refresh_tokens_endpoint(request: Request, current_admin: CurrentAdmin, service: FromDishka[ShowRefreshTokenCase], limit: int = 100, offset: int = 0) -> list[FullRefreshTokenInfoDTO]:
    return await service.show_refresh_tokens(limit, offset)


@admin_refresh_tokens_router.get('/active', response_model=list[FullRefreshTokenInfoDTO], summary='Show active refresh tokens')
@inject
async def show_active_refresh_tokens_endpoint(request: Request, current_admin: CurrentAdmin, service: FromDishka[ShowRefreshTokenCase], limit: int = 100, offset: int = 0) -> list[FullRefreshTokenInfoDTO]:
    return await service.show_active_refresh_tokens(limit, offset)


@admin_refresh_tokens_router.get('/revoked', response_model=list[FullRefreshTokenInfoDTO], summary='Show revoked refresh tokens')
@inject
async def show_revoked_refresh_tokens_endpoint(request: Request, current_admin: CurrentAdmin, service: FromDishka[ShowRefreshTokenCase], limit: int = 100, offset: int = 0) -> list[FullRefreshTokenInfoDTO]:
    return await service.show_revoked_refresh_tokens(limit, offset)


@admin_refresh_tokens_router.get('/by-id/{refresh_token_id}', response_model=FullRefreshTokenInfoDTO, summary='Show refresh token by id')
@inject
async def show_refresh_token_by_id_endpoint(request: Request, current_admin: CurrentAdmin, refresh_token_id: UUID, service: FromDishka[ShowRefreshTokenCase], limit: int = 100, offset: int = 0) -> FullRefreshTokenInfoDTO:
    return await service.show_refresh_token_by_id(refresh_token_id)


@admin_refresh_tokens_router.get('/by-user-id/{user_id}', response_model=list[FullRefreshTokenInfoDTO], summary='Show refresh tokens by user id')
@inject
async def show_refresh_tokens_by_user_id_endpoint(request: Request, current_admin: CurrentAdmin, user_id: UUID, service: FromDishka[ShowRefreshTokenCase], limit: int = 100, offset: int = 0) -> list[FullRefreshTokenInfoDTO]:
    return await service.show_refresh_tokens_by_user_id(user_id)


@admin_refresh_tokens_router.delete('/{refresh_token_id}', summary='Delete refresh token')
@limiter.limit('30/minute')
@inject
async def delete_refresh_token_endpoint(request: Request, current_admin: CurrentAdmin, refresh_token_id: UUID, service: FromDishka[DeleteRefreshTokenCase]) -> None:
    await service.delete_refresh_token(refresh_token_id)
