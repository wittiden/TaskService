from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, status
from starlette.requests import Request
from starlette.responses import Response

from app.common.limiter.config import limiter
from app.common.security.jwt_current import CurrentUser
from app.infrastructure.unit_of_work.uow import UnitOfWork
from app.modules.tasks.service.use_cases import (
    DeleteTaskCase,
)

delete_tasks_router = APIRouter(prefix='/api/v1/tasks', tags=['user-tasks'])


@delete_tasks_router.delete(
    '/closed-completed',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Delete close complete user tasks',
)
@limiter.limit('10/minute')
@inject
async def delete_close_complete_user_tasks_endpoint(
    request: Request,
    response: Response,
    current_user: CurrentUser,
    case: FromDishka[DeleteTaskCase],
    uow: FromDishka[UnitOfWork],
) -> None:
    await case.delete_close_complete_user_tasks(current_user.user_id)


@delete_tasks_router.delete(
    '/closed', status_code=status.HTTP_204_NO_CONTENT, summary='Delete close user tasks'
)
@limiter.limit('10/minute')
@inject
async def delete_close_user_tasks_endpoint(
    request: Request,
    response: Response,
    current_user: CurrentUser,
    case: FromDishka[DeleteTaskCase],
    uow: FromDishka[UnitOfWork],
) -> None:
    await case.delete_close_user_tasks(current_user.user_id)


@delete_tasks_router.delete(
    '/completed', status_code=status.HTTP_204_NO_CONTENT, summary='Delete complete user tasks'
)
@limiter.limit('10/minute')
@inject
async def delete_complete_user_tasks_endpoint(
    request: Request,
    response: Response,
    current_user: CurrentUser,
    case: FromDishka[DeleteTaskCase],
    uow: FromDishka[UnitOfWork],
) -> None:
    await case.delete_complete_user_tasks(current_user.user_id)


@delete_tasks_router.delete(
    '/', status_code=status.HTTP_204_NO_CONTENT, summary='Delete user tasks'
)
@limiter.limit('10/minute')
@inject
async def delete_user_tasks_endpoint(
    request: Request,
    response: Response,
    current_user: CurrentUser,
    case: FromDishka[DeleteTaskCase],
    uow: FromDishka[UnitOfWork],
) -> None:
    await case.delete_user_tasks(current_user.user_id)


@delete_tasks_router.delete(
    '/{task_id}', status_code=status.HTTP_204_NO_CONTENT, summary='Delete user task by id'
)
@limiter.limit('20/minute')
@inject
async def delete_user_task_by_id_endpoint(
    request: Request,
    response: Response,
    current_user: CurrentUser,
    task_id: UUID,
    case: FromDishka[DeleteTaskCase],
    uow: FromDishka[UnitOfWork],
) -> None:
    await case.delete_user_task_by_id(task_id, current_user.user_id)
