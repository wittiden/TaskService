from fastapi import APIRouter, Request
from dishka.integrations.fastapi import FromDishka, inject

from app.modules.users.contracts.dtos import SecurityUserInfoDTO
from app.modules.users.contracts.schemas import CreateUserSchema
from app.modules.users.service.use_cases import CreateUserCase

users_router = APIRouter(prefix='/api/v1/users', tags=['users'])
admin_users_router = APIRouter(prefix='/api/v1/admin/users', tags=['admin-users'])


@users_router.post('/standard', response_model=SecurityUserInfoDTO, summary='Create standard user')
@inject
async def create_standard_user_endpoint(request: Request, schema: CreateUserSchema, service: FromDishka[CreateUserCase]) -> SecurityUserInfoDTO:
    return await service.create_standard_user(schema.name, schema.email, schema.password)


@users_router.post('/vip', response_model=SecurityUserInfoDTO, summary='Create vip user')
@inject
async def create_vip_user_endpoint(request: Request, schema: CreateUserSchema, service: FromDishka[CreateUserCase]) -> SecurityUserInfoDTO:
    return await service.create_vip_user(schema.name, schema.email, schema.password)


@users_router.post('/admin', response_model=SecurityUserInfoDTO, summary='Create admin user')
@inject
async def create_admin_endpoint(request: Request, schema: CreateUserSchema, service: FromDishka[CreateUserCase]) -> SecurityUserInfoDTO:
    return await service.create_admin(schema.name, schema.email, schema.password)
