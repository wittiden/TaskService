from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import Response

from app.common.limiter.config import limiter
from app.common.security.jwt_current import CurrentAdmin
from app.infrastructure.unit_of_work.uow import UnitOfWork
from app.modules.audits.contracts.dtos import FullUserAuditInfoDTO
from app.modules.audits.service.use_cases import ShowUserAuditCase

admin_user_audits_router = APIRouter(prefix='/api/v1/admin/user-audits', tags=['admin-user-audits'])


@admin_user_audits_router.get(
    '/', response_model=list[FullUserAuditInfoDTO], summary='Show user audits'
)
@limiter.limit('30/minute')
@inject
async def show_user_audits_endpoint(
    request: Request,
    response: Response,
    current_user: CurrentAdmin,
    case: FromDishka[ShowUserAuditCase],
    uow: FromDishka[UnitOfWork],
    offset: int = 0,
    limit: int = 100,
) -> list[FullUserAuditInfoDTO]:
    return await case.show_user_audits(offset, limit)


@admin_user_audits_router.get(
    '/{user_id}',
    response_model=list[FullUserAuditInfoDTO],
    summary='Show user audits by user id',
)
@inject
async def show_user_audits_by_user_id_endpoint(
    current_user: CurrentAdmin,
    user_id: UUID,
    case: FromDishka[ShowUserAuditCase],
    uow: FromDishka[UnitOfWork],
    offset: int = 0,
    limit: int = 100,
) -> list[FullUserAuditInfoDTO]:
    return await case.show_user_audits_by_user_id(user_id, offset, limit)


@admin_user_audits_router.get(
    '/by-id/{user_audit_id}',
    response_model=FullUserAuditInfoDTO,
    summary='Show user audits by id',
)
@inject
async def show_user_audits_by_id_endpoint(
    current_user: CurrentAdmin,
    user_audit_id: UUID,
    case: FromDishka[ShowUserAuditCase],
    uow: FromDishka[UnitOfWork],
) -> FullUserAuditInfoDTO:
    return await case.show_user_audit_by_id(user_audit_id)
