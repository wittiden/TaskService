from typing import Annotated

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends

from app.infrastructure.database.models import UserModel
from app.modules.auth.service.use_cases import CurrentUserCase

security = HTTPBearer()


def get_token(creds: HTTPAuthorizationCredentials = Depends(security)) -> str:
    return creds.credentials


@inject
async def get_current_user(service: FromDishka[CurrentUserCase], token: str = Depends(get_token)) -> UserModel:
    return await service.show_current_user(token)


@inject
async def get_current_admin(service: FromDishka[CurrentUserCase], token: str = Depends(get_token)) -> UserModel:
    return await service.show_current_admin(token)


CurrentUser = Annotated[UserModel, Depends(get_current_user)]
CurrentAdmin = Annotated[UserModel, Depends(get_current_admin)]
