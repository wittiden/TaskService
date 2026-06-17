from typing import Annotated

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends

from app.modules.auth.service.use_cases import CurrentUserCase
from app.modules.users.contracts.dtos import UserInfoDTO

security = HTTPBearer()


def get_token(creds: HTTPAuthorizationCredentials = Depends(security)) -> str:
    return creds.credentials


@inject
async def get_current_user(service: FromDishka[CurrentUserCase], token: str = Depends(get_token)) -> UserInfoDTO:
    return await service.show_current_user(token)


@inject
async def get_current_admin(service: FromDishka[CurrentUserCase], token: str = Depends(get_token)) -> UserInfoDTO:
    return await service.show_current_admin(token)


@inject
async def get_current_vip(service: FromDishka[CurrentUserCase], token: str = Depends(get_token)) -> UserInfoDTO:
    return await service.show_current_vip(token)


CurrentUser = Annotated[UserInfoDTO, Depends(get_current_user)]
CurrentAdmin = Annotated[UserInfoDTO, Depends(get_current_admin)]
CurrentVip = Annotated[UserInfoDTO, Depends(get_current_vip)]
