from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import Response

from app.common.limiter.config import limiter
from app.common.security.jwt_current import CurrentUser
from app.infrastructure.unit_of_work.uow import UnitOfWork
from app.modules.tasks.contracts.dtos import FullTaskInfoDTO
from app.modules.tasks.contracts.schemas import UpdateTaskSchema
from app.modules.tasks.service.use_cases import (
    ManageTaskCase,
    UpdateTaskCase,
)

update_tasks_router = APIRouter(prefix='/api/v1/tasks', tags=['user-tasks'])


@update_tasks_router.patch(
    '/close/{task_id}', response_model=FullTaskInfoDTO, summary='Close my task'
)
@limiter.limit('10/minute')
@inject
async def close_my_task_endpoint(
    request: Request,
    response: Response,
    current_user: CurrentUser,
    task_id: UUID,
    case: FromDishka[ManageTaskCase],
    uow: FromDishka[UnitOfWork],
) -> FullTaskInfoDTO:
    return await case.close_my_task(current_user.user_id, task_id)


@update_tasks_router.patch(
    '/complete/{task_id}', response_model=FullTaskInfoDTO, summary='Complete my task'
)
@limiter.limit('10/minute')
@inject
async def complete_my_task_endpoint(
    request: Request,
    response: Response,
    current_user: CurrentUser,
    task_id: UUID,
    case: FromDishka[ManageTaskCase],
    uow: FromDishka[UnitOfWork],
) -> FullTaskInfoDTO:
    return await case.complete_my_task(current_user.user_id, task_id)


@update_tasks_router.patch('/{task_id}', response_model=FullTaskInfoDTO, summary='Update my task')
@limiter.limit('30/minute')
@inject
async def update_my_task_endpoint(
    request: Request,
    response: Response,
    current_user: CurrentUser,
    task_id: UUID,
    schema: UpdateTaskSchema,
    case: FromDishka[UpdateTaskCase],
    uow: FromDishka[UnitOfWork],
) -> FullTaskInfoDTO:
    return await case.update_my_task_params(
        current_user.user_id, task_id, schema.model_dump(exclude_none=True)
    )
