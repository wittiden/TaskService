from typing import Annotated

from starlette.requests import Request
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dishka.integrations.fastapi import FromDishka, inject

from app.modules.auth.service.use_cases import ShowCurrentUserCase
from app.modules.users.contracts.dtos import FullUserInfoDTO

security = HTTPBearer()


def get_token(creds: HTTPAuthorizationCredentials = Depends(security)) -> str:
    return creds.credentials


@inject
async def get_current_standard(request: Request, case: FromDishka[ShowCurrentUserCase], token: str = Depends(get_token)) -> FullUserInfoDTO:
    current_standard = await case.current_standard(token)
    request.state.user_id = current_standard.user_id
    return current_standard


@inject
async def get_current_admin(request: Request, case: FromDishka[ShowCurrentUserCase], token: str = Depends(get_token)) -> FullUserInfoDTO:
    current_admin = await case.current_admin(token)
    request.state.user_id = current_admin.user_id
    return current_admin


@inject
async def get_current_vip(request: Request, case: FromDishka[ShowCurrentUserCase], token: str = Depends(get_token)) -> FullUserInfoDTO:
    current_vip = await case.current_vip(token)
    request.state.user_id = current_vip.user_id
    return current_vip


CurrentUser = Annotated[FullUserInfoDTO, Depends(get_current_standard)]
CurrentAdmin = Annotated[FullUserInfoDTO, Depends(get_current_admin)]
CurrentVip= Annotated[FullUserInfoDTO, Depends(get_current_vip)]
