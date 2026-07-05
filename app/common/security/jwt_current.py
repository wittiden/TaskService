from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dishka.integrations.fastapi import FromDishka, inject

from app.modules.auth.service.use_cases import ShowCurrentUserCase
from app.modules.users.contracts.dtos import FullUserInfoDTO

security = HTTPBearer()


def get_token(creds: HTTPAuthorizationCredentials = Depends(security)) -> str:
    return creds.credentials


@inject
async def get_current_standard(case: FromDishka[ShowCurrentUserCase], token: str = Depends(get_token)) -> FullUserInfoDTO:
    return await case.current_standard(token)


@inject
async def get_current_admin(case: FromDishka[ShowCurrentUserCase], token: str = Depends(get_token)) -> FullUserInfoDTO:
    return await case.current_admin(token)


@inject
async def get_current_vip(case: FromDishka[ShowCurrentUserCase], token: str = Depends(get_token)) -> FullUserInfoDTO:
    return await case.current_vip(token)


CurrentStandard = Annotated[FullUserInfoDTO, Depends(get_current_standard)]
CurrentAdmin = Annotated[FullUserInfoDTO, Depends(get_current_admin)]
CurrentVip= Annotated[FullUserInfoDTO, Depends(get_current_vip)]
