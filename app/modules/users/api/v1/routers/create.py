from uuid import uuid4

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, status
from starlette.requests import Request
from starlette.responses import Response

from app.common.email_service.templates.create import create_user_body, create_user_subject
from app.common.limiter.config import limiter
from app.common.task_service.utils import celery
from app.infrastructure.unit_of_work.uow import UnitOfWork
from app.modules.users.contracts.dtos import SecurityUserInfoDTO
from app.modules.users.contracts.schemas import CreateUserSchema
from app.modules.users.service.use_cases import CreateUserCase

create_users_router = APIRouter(prefix='/api/v1/users', tags=['users'])


@create_users_router.post(
    '/standard',
    response_model=SecurityUserInfoDTO,
    summary='Create standard user',
    status_code=status.HTTP_201_CREATED,
)
@limiter.shared_limit('10/minute', scope='create_limit')
@inject
async def create_standard_endpoint(
    request: Request,
    response: Response,
    schema: CreateUserSchema,
    case: FromDishka[CreateUserCase],
    uow: FromDishka[UnitOfWork],
) -> SecurityUserInfoDTO:
    user = await case.create_standard(schema.name, schema.email, schema.password)

    if celery:
        task_id = str(uuid4())
        celery.send_task(
            'send_email',
            args=(schema.email, create_user_subject(schema.name), create_user_body(schema.name)),
            task_id=task_id,
        )
        response.headers['X-Task-ID'] = task_id

    return user


@create_users_router.post(
    '/admin',
    response_model=SecurityUserInfoDTO,
    summary='Create admin user',
    status_code=status.HTTP_201_CREATED,
)
@limiter.shared_limit('10/minute', scope='create_limit')
@inject
async def create_admin_endpoint(
    request: Request,
    response: Response,
    schema: CreateUserSchema,
    case: FromDishka[CreateUserCase],
    uow: FromDishka[UnitOfWork],
) -> SecurityUserInfoDTO:
    user = await case.create_admin(schema.name, schema.email, schema.password)

    if celery:
        task_id = str(uuid4())
        celery.send_task(
            'send_email',
            args=(schema.email, create_user_subject(schema.name), create_user_body(schema.name)),
            task_id=task_id,
        )
        response.headers['X-Task-ID'] = task_id

    return user


@create_users_router.post(
    '/vip',
    response_model=SecurityUserInfoDTO,
    summary='Create vip user',
    status_code=status.HTTP_201_CREATED,
)
@limiter.shared_limit('10/minute', scope='create_limit')
@inject
async def create_vip_endpoint(
    request: Request,
    response: Response,
    schema: CreateUserSchema,
    case: FromDishka[CreateUserCase],
    uow: FromDishka[UnitOfWork],
) -> SecurityUserInfoDTO:
    user = await case.create_vip(schema.name, schema.email, schema.password)

    if celery:
        task_id = str(uuid4())
        celery.send_task(
            'send_email',
            args=(schema.email, create_user_subject(schema.name), create_user_body(schema.name)),
            task_id=task_id,
        )
        response.headers['X-Task-ID'] = task_id

    return user
