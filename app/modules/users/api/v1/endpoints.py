from fastapi import APIRouter
from dishka.integrations.fastapi import inject, FromDishka

from app.modules.users.contracts.dtos import SecurityUserInfoDTO
from app.modules.users.contracts.schemas import CreateUserSchema
from app.modules.users.service.use_cases import CreateUserCase

users_router = APIRouter(prefix='/api/v1/users', tags=['users'])
admin_users_router = APIRouter(prefix='/api/v1/admin/users', tags=['admin-users'])
vip_users_router = APIRouter(prefix='/api/v1/admin/users', tags=['admin-users'])



@inject
@users_router.post('/standard', response_model=SecurityUserInfoDTO, summary='Create standard user')
async def create_standard_endpoint(schema: CreateUserSchema, case: FromDishka[CreateUserCase]) -> SecurityUserInfoDTO:
    return await case.create_standard(schema.name, schema.email, schema.password)


@inject
@users_router.post('/admin', response_model=SecurityUserInfoDTO, summary='Create admin user')
async def create_admin_endpoint(schema: CreateUserSchema, case: FromDishka[CreateUserCase]) -> SecurityUserInfoDTO:
    return await case.create_admin(schema.name, schema.email, schema.password)


@inject
@users_router.post('/vip', response_model=SecurityUserInfoDTO, summary='Create vip user')
async def create_standard_endpoint(schema: CreateUserSchema, case: FromDishka[CreateUserCase]) -> SecurityUserInfoDTO:
    return await case.create_vip(schema.name, schema.email, schema.password)
