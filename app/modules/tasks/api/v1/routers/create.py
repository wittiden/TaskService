from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, status
from starlette.requests import Request
from starlette.responses import Response

from app.common.limiter.config import limiter
from app.common.security.jwt_current import CurrentUser
from app.infrastructure.unit_of_work.uow import UnitOfWork
from app.modules.tasks.contracts.dtos import SecurityTaskInfoDTO
from app.modules.tasks.contracts.schemas import CreateTaskSchema
from app.modules.tasks.service.use_cases import (
    CreateTaskCase,
)

create_tasks_router = APIRouter(prefix='/api/v1/tasks', tags=['user-tasks'])


@create_tasks_router.post(
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
