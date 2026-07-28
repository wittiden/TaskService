from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter

from app.common.security.jwt_current import CurrentUser
from app.infrastructure.unit_of_work.uow import UnitOfWork
from app.modules.tasks.contracts.dtos import FullTaskInfoDTO, SecurityTaskInfoDTO
from app.modules.tasks.service.use_cases import (
    ShowTaskCase,
)

read_tasks_router = APIRouter(prefix='/api/v1/tasks', tags=['user-tasks'])


@read_tasks_router.get('/', response_model=list[SecurityTaskInfoDTO], summary='Show user tasks')
@inject
async def show_user_tasks_endpoint(
    current_user: CurrentUser,
    case: FromDishka[ShowTaskCase],
    uow: FromDishka[UnitOfWork],
    offset: int = 0,
    limit: int = 100,
) -> list[SecurityTaskInfoDTO]:
    return await case.show_user_tasks(current_user.user_id, offset, limit)


@read_tasks_router.get(
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


@read_tasks_router.get(
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


@read_tasks_router.get(
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


@read_tasks_router.get('/{task_id}', response_model=FullTaskInfoDTO, summary='Show user task by id')
@inject
async def show_user_task_by_id_endpoint(
    current_user: CurrentUser,
    task_id: UUID,
    case: FromDishka[ShowTaskCase],
    uow: FromDishka[UnitOfWork],
) -> FullTaskInfoDTO:
    return await case.show_user_task_by_id(task_id, current_user.user_id)
