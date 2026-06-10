from uuid import UUID

from fastapi import APIRouter, Request
from dishka.integrations.fastapi import FromDishka, inject

from app.common.limiter.limit import limiter
from app.common.security.jwt_current import CurrentUser, CurrentAdmin
from app.modules.users.contracts.dtos import SecurityUserInfoDTO, FullUserInfoDTO
from app.modules.users.contracts.schemas import CreateUserSchema, UpdateUserSchema
from app.modules.users.service.use_cases import CreateUserCase, UpdateUserCase, DeleteUserCase, ShowUserCase, \
    ManageUserCase

users_router = APIRouter(prefix='/api/v1/users', tags=['users'])
admin_users_router = APIRouter(prefix='/api/v1/admin/users', tags=['admin-users'])


@users_router.post('/', response_model=SecurityUserInfoDTO, summary='Create standard user')
@limiter.limit('10/minute')
@inject
async def create_standard_user_endpoint(request: Request, schema: CreateUserSchema, service: FromDishka[CreateUserCase]) -> SecurityUserInfoDTO:
    return await service.create_standard_user(schema.name, schema.email, schema.password)


@users_router.post('/vip', response_model=SecurityUserInfoDTO, summary='Create vip user')
@limiter.limit('10/minute')
@inject
async def create_vip_user_endpoint(request: Request, schema: CreateUserSchema, service: FromDishka[CreateUserCase]) -> SecurityUserInfoDTO:
    return await service.create_vip_user(schema.name, schema.email, schema.password)


@users_router.post('/admin', response_model=SecurityUserInfoDTO, summary='Create admin user')
@limiter.limit('5/minute')
@inject
async def create_admin_endpoint(request: Request, schema: CreateUserSchema, service: FromDishka[CreateUserCase]) -> SecurityUserInfoDTO:
    return await service.create_admin(schema.name, schema.email, schema.password)


@users_router.patch('/', response_model=SecurityUserInfoDTO, summary='Partial update user')
@limiter.limit('10/minute')
@inject
async def partial_update_user_data_endpoint(request: Request, current_user: CurrentUser, schema: UpdateUserSchema, service: FromDishka[UpdateUserCase]) -> SecurityUserInfoDTO:
    return await service.partial_user_data(current_user, schema.model_dump())


@users_router.delete('/me', summary='Close my user')
@limiter.limit('3/minute')
@inject
async def close_my_user_endpoint(request: Request, current_user: CurrentUser, service: FromDishka[DeleteUserCase]) -> None:
    await service.close_user(current_user)


@admin_users_router.delete('/{user_id}', summary='Delete user by id')
@limiter.limit('10/minute')
@inject
async def delete_user_by_id_endpoint(request: Request, current_admin: CurrentAdmin, user_id: UUID, service: FromDishka[DeleteUserCase]) -> None:
    await service.delete_user(user_id)


@admin_users_router.get('/', response_model=list[FullUserInfoDTO], summary='Show users')
@inject
async def show_users_endpoint(request: Request, current_admin: CurrentAdmin, service: FromDishka[ShowUserCase], limit: int = 100, offset: int = 0) -> list[FullUserInfoDTO]:
    return await service.show_users(limit, offset)


@admin_users_router.get('/by-id/{user_id}', response_model=FullUserInfoDTO, summary='Show user by id')
@inject
async def show_user_by_id_endpoint(request: Request, current_admin: CurrentAdmin, user_id: UUID, service: FromDishka[ShowUserCase]) -> FullUserInfoDTO:
    return await service.show_user_by_id(user_id)


@users_router.get('/by-email/{email}', response_model=SecurityUserInfoDTO, summary='Show user by email')
@inject
async def show_user_by_email(request: Request, current_user: CurrentUser, email: str, service: FromDishka[ShowUserCase]) -> SecurityUserInfoDTO:
    return await service.show_user_by_email(email)


@users_router.get('/me', response_model=SecurityUserInfoDTO, summary='Show my user')
@limiter.limit('30/minute')
@inject
async def show_my_user_endpoint(request: Request, current_user: CurrentUser, service: FromDishka[ShowUserCase]) -> SecurityUserInfoDTO:
    return await service.show_my_user(current_user)


@admin_users_router.patch('/block/{user_id}', summary='Block user')
@limiter.shared_limit('20/minute', scope='manage_user_case')
@inject
async def block_user_endpoint(request: Request, current_admin: CurrentAdmin, user_id: UUID, service: FromDishka[ManageUserCase]) -> None:
    await service.block_user(user_id)


@admin_users_router.patch('/unblock/{user_id}', summary='Unblock user')
@limiter.shared_limit('20/minute', scope='manage_user_case')
@inject
async def unblock_user_endpoint(request: Request, current_admin: CurrentAdmin, user_id: UUID, service: FromDishka[ManageUserCase]) -> None:
    await service.unblock_user(user_id)
