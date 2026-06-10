from typing import Any
from datetime import datetime, UTC, timedelta
from uuid import uuid4, UUID

import jwt
from jwt import InvalidTokenError, ExpiredSignatureError, InvalidAudienceError

from app.common.enums.auth import TokenTypeEnum
from app.common.enums.users import UserRoleEnum
from app.common.security.jwt_config import JWTConfig
from app.common.security.pass_utils import verify_pass
from app.infrastructure.database.models import UserModel
from app.modules.auth.contracts.dtos import TokensInfoDTO, FullRefreshTokenInfoDTO
from app.modules.auth.exceptions import InvalidTokenVersionError, ForbiddenError, RevokedTokenError, TokenInvalidError, \
    ExpiredTokenError, InvalidTokenAudienceError, TokenRetentionPeriodError
from app.modules.auth.repository.commands import RefreshTokenCommandsRepository
from app.modules.auth.repository.queries import RefreshTokenQueriesRepository
from app.modules.auth.service.guards import AuthGuards
from app.modules.users.repository.queries import UserQueriesRepository
from app.modules.users.service.guards import UserGuards
from app.infrastructure.database.models.refresh_token import RefreshTokenModel


class ManageTokenCase:
    """Кейс по менедженгу токенов"""

    def __init__(self, jwt_config: JWTConfig, refresh_token_commands: RefreshTokenCommandsRepository) -> None:
        self._jwt_config = jwt_config
        self._refresh_token_commands = refresh_token_commands

    def encode_access_token(self, payload: dict[str, Any]) -> str:
        now = datetime.now(UTC)
        token_id = str(uuid4())

        return jwt.encode(
            algorithm=self._jwt_config.ACCESS_TOKEN_ALGORITHM,
            key=self._jwt_config.access_token_private_key,
            payload={
                **payload,
                'jti': token_id,
                'iat': now,
                'exp': now + timedelta(minutes=self._jwt_config.ACCESS_TOKEN_EXPIRE_MINUTES),
                'token_type': TokenTypeEnum.ACCESS_TOKEN,
                'aud': self._jwt_config.ACCESS_TOKEN_AUDIENCE,
            }
        )

    def decode_access_token(self, access_token: str) -> dict[str, Any]:
        try:
            return jwt.decode(
                access_token,
                algorithms=[self._jwt_config.ACCESS_TOKEN_ALGORITHM,],
                key=self._jwt_config.access_token_public_key,
                audience=self._jwt_config.ACCESS_TOKEN_AUDIENCE,
            )
        except ExpiredSignatureError:
            raise ExpiredTokenError('Expired token signature error')
        except InvalidAudienceError:
            raise InvalidTokenAudienceError('Invalid token audience error')
        except InvalidTokenError:
            raise TokenInvalidError('Token invalid error')


    async def encode_refresh_token(self, payload: dict[str, Any]) -> str:
        now = datetime.now(UTC)
        token_id = str(uuid4())

        token_payload: dict[str, Any] = {
            **payload,
            'jti': token_id,
            'iat': now,
            'exp': now + timedelta(days=self._jwt_config.REFRESH_TOKEN_EXPIRE_DAYS),
            'token_type': TokenTypeEnum.REFRESH_TOKEN,
            'token_version': self._jwt_config.REFRESH_TOKEN_VERSION,
            'aud': self._jwt_config.REFRESH_TOKEN_AUDIENCE,
        }

        obj = RefreshTokenModel(
            refresh_token_id=token_payload['jti'],
            user_id=token_payload['sub'],
            expires_at=token_payload['exp'],
            issued_at=token_payload['iat'],
            version=token_payload['token_version'],
            audience=token_payload['aud'],
        )

        await self._refresh_token_commands.insert_refresh_token_data(obj)

        return jwt.encode(
            payload=token_payload,
            algorithm=self._jwt_config.REFRESH_TOKEN_ALGORITHM,
            key=self._jwt_config.refresh_token_private_key,
        )

    def decode_refresh_token(self, refresh_token: str) -> dict[str, Any]:
        try:
            return jwt.decode(
                refresh_token,
                algorithms=[self._jwt_config.REFRESH_TOKEN_ALGORITHM,],
                key=self._jwt_config.refresh_token_public_key,
                audience=self._jwt_config.REFRESH_TOKEN_AUDIENCE,
            )
        except ExpiredSignatureError:
            raise ExpiredTokenError('Expired token signature error')
        except InvalidAudienceError:
            raise InvalidTokenAudienceError('Invalid token audience error')
        except InvalidTokenError:
            raise TokenInvalidError('Token invalid error')


class AuthUserCase:
    """Кейс по аутентификации пользователя"""

    def __init__(self, user_queries: UserQueriesRepository, manage_token_case: ManageTokenCase, refresh_token_commands: RefreshTokenCommandsRepository, refresh_token_queries: RefreshTokenQueriesRepository, jwt_config: JWTConfig) -> None:
        self._user_queries = user_queries
        self._manage_token_case = manage_token_case
        self._refresh_token_commands = refresh_token_commands
        self._refresh_token_queries = refresh_token_queries
        self._jwt_config = jwt_config

    async def login_user(self, email: str, password: str) -> TokensInfoDTO:
        user = await self._user_queries.select_user_by_email(email)
        user = UserGuards.require_user_is_exist(user)

        verify_pass(password, user.password_hash)

        access_payload = {
            'sub': str(user.user_id),
            'role': user.role,
        }

        refresh_payload = {
            'sub': str(user.user_id),
        }

        access_token = self._manage_token_case.encode_access_token(access_payload)
        refresh_token = await self._manage_token_case.encode_refresh_token(refresh_payload)

        return TokensInfoDTO(access_token=access_token, refresh_token=refresh_token)

    async def logout(self, current_user: UserModel) -> None:
        now = datetime.now(UTC)

        new_data = {
            'revoked_at': now
        }

        objs = await self._refresh_token_queries.select_refresh_tokens_by_user_id(current_user.user_id)

        for obj in objs:
            await self._refresh_token_commands.alter_refresh_token_data(obj, new_data)

    async def refresh(self, refresh_token: str) -> TokensInfoDTO:
        payload = self._manage_token_case.decode_refresh_token(refresh_token)

        token_type = payload['token_type']
        AuthGuards.require_refresh_token_type(token_type)

        if not payload['token_version'] >= self._jwt_config.REFRESH_TOKEN_VERSION:
            raise InvalidTokenVersionError('Old token version error')

        refresh_token_id = payload['jti']
        obj = await self._refresh_token_queries.select_refresh_token_by_id(refresh_token_id)

        if obj.revoked_at is not None:
            raise RevokedTokenError('Token was burned error')

        user_id = payload['sub']
        user = await self._user_queries.select_user_by_id(user_id)

        now = datetime.now(UTC)
        new_data = {
            'revoked_at': now
        }
        await self._refresh_token_commands.alter_refresh_token_data(obj, new_data)

        access_payload = {
            'sub': user.user_id,
            'role': user.role,
        }
        refresh_payload = {
            'sub': user.user_id,
        }
        access_token = self._manage_token_case.encode_access_token(access_payload)
        refresh_token = await self._manage_token_case.encode_refresh_token(refresh_payload)

        return TokensInfoDTO(access_token=access_token, refresh_token=refresh_token)


class CurrentUserCase:
    """Кейс по получению текущего пользователя"""

    def __init__(self, user_queries: UserQueriesRepository, manage_token_case: ManageTokenCase) -> None:
        self._user_queries = user_queries
        self._manage_token_case = manage_token_case

    async def _current(self, access_token: str, require_admin: bool = False, require_vip: bool = False) -> UserModel:
        payload = self._manage_token_case.decode_access_token(access_token)
        token_type = payload['token_type']
        AuthGuards.require_access_token_type(token_type)

        if require_admin:
            if not payload['role'] == UserRoleEnum.ADMIN:
                raise ForbiddenError('Invalid user role error')

        if require_vip:
            if payload['role'] not in (UserRoleEnum.ADMIN, UserRoleEnum.VIP_USER):
                raise ForbiddenError('Invalid user role error')

        user_id = payload['sub']
        user = await self._user_queries.select_user_by_id(user_id)
        user = UserGuards.require_user_is_exist(user)

        return user

    async def show_current_user(self, access_token: str) -> UserModel:
        return await self._current(access_token)

    async def show_current_vip(self, access_token: str) -> UserModel:
        return await self._current(access_token, require_vip=True)

    async def show_current_admin(self, access_token: str) -> UserModel:
        return await self._current(access_token, require_admin=True)


class ShowRefreshTokenCase:
    """Кейс по показу токенов"""

    def __init__(self, refresh_token_queries: RefreshTokenQueriesRepository) -> None:
        self._refresh_token_queries = refresh_token_queries

    async def show_refresh_tokens(self, limit: int = 100, offset: int = 0) -> list[FullRefreshTokenInfoDTO]:
        objs = await self._refresh_token_queries.select_refresh_tokens(limit, offset)
        return [FullRefreshTokenInfoDTO.model_validate(obj) for obj in  objs]

    async def show_active_refresh_tokens(self, limit: int = 100, offset: int = 0) -> list[FullRefreshTokenInfoDTO]:
        objs = await self._refresh_token_queries.select_active_refresh_tokens(limit, offset)
        return [FullRefreshTokenInfoDTO.model_validate(obj) for obj in  objs]

    async def show_revoked_refresh_tokens(self, limit: int = 100, offset: int = 0) -> list[FullRefreshTokenInfoDTO]:
        objs = await self._refresh_token_queries.select_revoked_refresh_tokens(limit, offset)
        return [FullRefreshTokenInfoDTO.model_validate(obj) for obj in  objs]

    async def show_refresh_token_by_id(self, refresh_token_id: UUID) -> FullRefreshTokenInfoDTO:
        obj = await self._refresh_token_queries.select_refresh_token_by_id(refresh_token_id)
        obj = AuthGuards.require_refresh_token(obj)
        return FullRefreshTokenInfoDTO.model_validate(obj)

    async def show_refresh_tokens_by_user_id(self, user_id: UUID) -> list[FullRefreshTokenInfoDTO]:
        objs = await self._refresh_token_queries.select_refresh_tokens_by_user_id(user_id)
        return [FullRefreshTokenInfoDTO.model_validate(obj) for obj in  objs]


class DeleteRefreshTokenCase:
    """Кейс по удалению токенов из бд"""

    def __init__(self, refresh_token_queries: RefreshTokenQueriesRepository, refresh_token_commands: RefreshTokenCommandsRepository, jwt_config: JWTConfig) -> None:
        self._refresh_token_commands = refresh_token_commands
        self._refresh_token_queries = refresh_token_queries
        self._jwt_config = jwt_config

    async def delete_refresh_token(self, refresh_token_id: UUID) -> None:
        refresh_token = await self._refresh_token_queries.select_refresh_token_by_id(refresh_token_id)
        refresh_token = AuthGuards.require_refresh_token(refresh_token)

        now = datetime.now(UTC)

        if not now >= refresh_token.expires_at + timedelta(days=self._jwt_config.REFRESH_TOKEN_RETENTION_DAYS):
            raise TokenRetentionPeriodError('Refresh token retention period error')

        await self._refresh_token_commands.delete_refresh_token(refresh_token)
