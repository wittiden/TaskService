from uuid import UUID

from fastapi import APIRouter, status
from dishka.integrations.fastapi import inject, FromDishka
from starlette.requests import Request
from starlette.responses import Response

from app.common.limiter.config import limiter
from app.infrastructure.unit_of_work.uow import UnitOfWork
from app.modules.users.contracts.dtos import SecurityUserInfoDTO, FullUserInfoDTO
from app.modules.users.contracts.schemas import CreateUserSchema, UpdateUserSchema
from app.modules.users.service.use_cases import CreateUserCase, DeleteUserCase, ManageUserCase, ShowUserCase, \
    UpdateUserCase
from app.common.security.jwt_current import CurrentUser, CurrentAdmin

users_router = APIRouter(prefix='/api/v1/users', tags=['users'])
admin_users_router = APIRouter(prefix='/api/v1/admin/users', tags=['admin-users'])


@users_router.post('/standard', response_model=SecurityUserInfoDTO, summary='Create standard user', status_code=status.HTTP_201_CREATED)
@limiter.shared_limit('10/minute', scope='create_limit')
@inject
async def create_standard_endpoint(request: Request, response: Response, schema: CreateUserSchema, case: FromDishka[CreateUserCase], uow: FromDishka[UnitOfWork]) -> SecurityUserInfoDTO:
    return await case.create_standard(schema.name, schema.email, schema.password)


@users_router.post('/admin', response_model=SecurityUserInfoDTO, summary='Create admin user', status_code=status.HTTP_201_CREATED)
@limiter.shared_limit('10/minute', scope='create_limit')
@inject
async def create_admin_endpoint(request: Request, response: Response, schema: CreateUserSchema, case: FromDishka[CreateUserCase], uow: FromDishka[UnitOfWork]) -> SecurityUserInfoDTO:
    return await case.create_admin(schema.name, schema.email, schema.password)


@users_router.post('/vip', response_model=SecurityUserInfoDTO, summary='Create vip user', status_code=status.HTTP_201_CREATED)
@limiter.shared_limit('10/minute', scope='create_limit')
@inject
async def create_standard_endpoint(request: Request, response: Response, schema: CreateUserSchema, case: FromDishka[CreateUserCase], uow: FromDishka[UnitOfWork]) -> SecurityUserInfoDTO:
    return await case.create_vip(schema.name, schema.email, schema.password)


@users_router.patch('/me', response_model=SecurityUserInfoDTO, summary='Update me')
@limiter.limit('10/minute')
@inject
async def update_me_endpoint(request: Request, response: Response, current_user: CurrentUser, schema: UpdateUserSchema, case: FromDishka[UpdateUserCase], uow: FromDishka[UnitOfWork]) -> SecurityUserInfoDTO:
    return await case.update_user_params(current_user, schema.model_dump(exclude_none=True))


@users_router.patch('/close-me', summary='Close my account', status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit('5/minute')
@inject
async def close_my_account_endpoint(request: Request, response: Response, current_user: CurrentUser, case: FromDishka[DeleteUserCase], uow: FromDishka[UnitOfWork]) -> None:
    await case.close_my_account(current_user)


@admin_users_router.delete('/{user_id}', summary='Delete user account', status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit('10/minute')
@inject
async def delete_user_account_endpoint(request: Request, response: Response, current_user: CurrentAdmin, user_id: UUID, case: FromDishka[DeleteUserCase], uow: FromDishka[UnitOfWork]) -> None:
    await case.delete_user_account(user_id)


@admin_users_router.patch('/block/{user_id}', response_model=FullUserInfoDTO, summary='Block user account')
@limiter.shared_limit('10/minute', scope='block_limit')
@inject
async def block_user_account_endpoint(request: Request, response: Response, current_user: CurrentAdmin, user_id: UUID, case: FromDishka[ManageUserCase], uow: FromDishka[UnitOfWork]) -> FullUserInfoDTO:
    return await case.block_user(user_id)


@admin_users_router.patch('/unblock/{user_id}', response_model=FullUserInfoDTO, summary='Unblock user account')
@limiter.shared_limit('10/minute', scope='block_limit')
@inject
async def unblock_user_account_endpoint(request: Request, response: Response, current_user: CurrentAdmin, user_id: UUID, case: FromDishka[ManageUserCase], uow: FromDishka[UnitOfWork]) -> FullUserInfoDTO:
    return await case.unblock_user(user_id)


@users_router.get('/me', response_model=SecurityUserInfoDTO, summary='Show me')
@inject
async def show_me_endpoint(current_user: CurrentUser, case: FromDishka[ShowUserCase], uow: FromDishka[UnitOfWork]) -> SecurityUserInfoDTO:
    return await case.show_me(current_user)


@admin_users_router.get('/by-id/{user_id}', response_model=FullUserInfoDTO, summary='Show user by id')
@inject
async def show_user_by_id_endpoint(current_user: CurrentAdmin, user_id: UUID, case: FromDishka[ShowUserCase], uow: FromDishka[UnitOfWork]) -> FullUserInfoDTO:
    return await case.show_user_by_id(user_id)


@admin_users_router.get('/', response_model=list[FullUserInfoDTO], summary='Show users')
@inject
async def show_users_endpoint(current_user: CurrentAdmin, case: FromDishka[ShowUserCase], uow: FromDishka[UnitOfWork], offset: int = 0, limit: int = 100) -> list[FullUserInfoDTO]:
    return await case.show_users(offset, limit)
