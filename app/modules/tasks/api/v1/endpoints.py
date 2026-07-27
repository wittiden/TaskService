from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, status
from starlette.requests import Request
from starlette.responses import Response

from app.common.limiter.config import limiter
from app.common.security.jwt_current import CurrentUser
from app.infrastructure.unit_of_work.uow import UnitOfWork
from app.modules.tasks.contracts.dtos import FullTaskInfoDTO, SecurityTaskInfoDTO
from app.modules.tasks.contracts.schemas import CreateTaskSchema, UpdateTaskSchema
from app.modules.tasks.service.use_cases import (
    CreateTaskCase,
    DeleteTaskCase,
    ManageTaskCase,
    ShowTaskCase,
    UpdateTaskCase,
)

tasks_router = APIRouter(prefix='/api/v1/tasks', tags=['user-tasks'])


@tasks_router.post(
    '/',
    response_model=SecurityTaskInfoDTO,
    status_code=status.HTTP_201_CREATED,
    summary='Create task',
)
@limiter.limit('20/minute')
@inject
async def create_task_endpoint(
    request: Request,
    response: Response,
    current_user: CurrentUser,
    schema: CreateTaskSchema,
    case: FromDishka[CreateTaskCase],
    uow: FromDishka[UnitOfWork],
) -> SecurityTaskInfoDTO:
    return await case.create_task(
        current_user, schema.important_level, schema.schedule_type, schema.title, schema.description
    )


@tasks_router.patch('/{task_id}', response_model=FullTaskInfoDTO, summary='Update my task')
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


@tasks_router.delete(
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
    return await case.delete_user_task_by_id(task_id, current_user.user_id)


@tasks_router.delete('/', status_code=status.HTTP_204_NO_CONTENT, summary='Delete user tasks')
@limiter.limit('10/minute')
@inject
async def delete_user_tasks_endpoint(
    request: Request,
    response: Response,
    current_user: CurrentUser,
    case: FromDishka[DeleteTaskCase],
    uow: FromDishka[UnitOfWork],
) -> None:
    return await case.delete_user_tasks(current_user.user_id)


@tasks_router.delete(
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
    return await case.delete_close_complete_user_tasks(current_user.user_id)


@tasks_router.delete(
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
    return await case.delete_close_user_tasks(current_user.user_id)


@tasks_router.delete(
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
    return await case.delete_complete_user_tasks(current_user.user_id)


@tasks_router.patch('/close/{task_id}', response_model=FullTaskInfoDTO, summary='Close my task')
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


@tasks_router.patch(
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


@tasks_router.get('/{task_id}', response_model=FullTaskInfoDTO, summary='Show user task by id')
@inject
async def show_user_task_by_id_endpoint(
    current_user: CurrentUser,
    task_id: UUID,
    case: FromDishka[ShowTaskCase],
    uow: FromDishka[UnitOfWork],
) -> FullTaskInfoDTO:
    return await case.show_user_task_by_id(task_id, current_user.user_id)


@tasks_router.get('/', response_model=list[SecurityTaskInfoDTO], summary='Show user tasks')
@inject
async def show_user_tasks_endpoint(
    current_user: CurrentUser,
    case: FromDishka[ShowTaskCase],
    uow: FromDishka[UnitOfWork],
    offset: int = 0,
    limit: int = 100,
) -> list[SecurityTaskInfoDTO]:
    return await case.show_user_tasks(current_user.user_id, offset, limit)


@tasks_router.get(
    '/completed', response_model=list[SecurityTaskInfoDTO], summary='Show user completed tasks'
)
@inject
async def show_user_completed_tasks_endpoint(
    current_user: CurrentUser,
    case: FromDishka[ShowTaskCase],
    uow: FromDishka[UnitOfWork],
    offset: int = 0,
    limit: int = 100,
) -> list[SecurityTaskInfoDTO]:
    return await case.show_user_completed_tasks(current_user.user_id, offset, limit)


@tasks_router.get(
    '/closed', response_model=list[SecurityTaskInfoDTO], summary='Show user closed tasks'
)
@inject
async def show_user_closed_tasks_endpoint(
    current_user: CurrentUser,
    case: FromDishka[ShowTaskCase],
    uow: FromDishka[UnitOfWork],
    offset: int = 0,
    limit: int = 100,
) -> list[SecurityTaskInfoDTO]:
    return await case.show_user_closed_tasks(current_user.user_id, offset, limit)


@tasks_router.get(
    '/active', response_model=list[SecurityTaskInfoDTO], summary='Show user active tasks'
)
@inject
async def show_user_active_tasks_endpoint(
    current_user: CurrentUser,
    case: FromDishka[ShowTaskCase],
    uow: FromDishka[UnitOfWork],
    offset: int = 0,
    limit: int = 100,
) -> list[SecurityTaskInfoDTO]:
    return await case.show_user_active_tasks(current_user.user_id, offset, limit)
