from fastapi import APIRouter
from dishka.integrations.fastapi import inject, FromDishka
from starlette.requests import Request
from starlette.responses import Response

from app.common.limiter.config import limiter
from app.modules.users.contracts.dtos import SecurityUserInfoDTO
from app.modules.users.contracts.schemas import CreateUserSchema
from app.modules.users.service.use_cases import CreateUserCase

users_router = APIRouter(prefix='/api/v1/users', tags=['users'])
admin_users_router = APIRouter(prefix='/api/v1/admin/users', tags=['admin-users'])
vip_users_router = APIRouter(prefix='/api/v1/admin/users', tags=['vip-users'])


@limiter.shared_limit('10/minute', scope='create_limit')
@users_router.post('/standard', response_model=SecurityUserInfoDTO, summary='Create standard user')
@inject
async def create_standard_endpoint(request: Request, response: Response, schema: CreateUserSchema, case: FromDishka[CreateUserCase]) -> SecurityUserInfoDTO:
    return await case.create_standard(schema.name, schema.email, schema.password)


@limiter.shared_limit('10/minute', scope='create_limit')
@users_router.post('/admin', response_model=SecurityUserInfoDTO, summary='Create admin user')
@inject
async def create_admin_endpoint(request: Request, response: Response, schema: CreateUserSchema, case: FromDishka[CreateUserCase]) -> SecurityUserInfoDTO:
    return await case.create_admin(schema.name, schema.email, schema.password)


@limiter.shared_limit('10/minute', scope='create_limit')
@users_router.post('/vip', response_model=SecurityUserInfoDTO, summary='Create vip user')
@inject
async def create_standard_endpoint(request: Request, response: Response, schema: CreateUserSchema, case: FromDishka[CreateUserCase]) -> SecurityUserInfoDTO:
    return await case.create_vip(schema.name, schema.email, schema.password)
