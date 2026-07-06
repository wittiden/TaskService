from typing import Any
from datetime import datetime, UTC, timedelta
from uuid import uuid4, UUID

import jwt
from jwt import InvalidSignatureError, InvalidAudienceError, InvalidAlgorithmError, InvalidKeyError, DecodeError, \
    InvalidTokenError

from app.infrastructure.redis.repositories.current_user.commands import CurrentUserRedisCommandsRepository
from app.modules.auth.jwt_config import TokenConfig
from app.modules.auth.exceptions import InvalidTokenSignatureError, InvalidTokenAudienceError, \
    InvalidTokenAlgorithmError, InvalidTokenKeyError, DecodeTokenError, TokenInvalidError, InvalidTokenVersionError, \
    RevokedTokenError
from app.common.enums.user import UserRoleEnum
from app.common.security.pass_utils import verify_pass
from app.modules.auth.contracts.dtos import TokenInfoDTO
from app.modules.auth.exceptions import ForbiddenError
from app.modules.auth.repository.commands import AuthCommandsRepository
from app.modules.auth.repository.queries import AuthQueriesRepository
from app.modules.users.contracts.dtos import FullUserInfoDTO
from app.modules.users.service.guards import UserGuards


class ManageTokenCase:
    """Кейс по менедженгу токенов"""

    def __init__(self, token_config: TokenConfig, auth_commands: AuthCommandsRepository) -> None:
        self._token_config = token_config
        self._auth_commands = auth_commands

    def encode_access_token(self, payload: dict[str, Any]) -> str:
        now = datetime.now(UTC)
        token_id = uuid4()
        payload = {
            **payload,
            'jti': str(token_id),
            'iat': now,
            'exp': now + timedelta(minutes=self._token_config.ACCESS_TOKEN_EXPIRE_MINUTES),
            'aud': self._token_config.ACCESS_TOKEN_AUDIENCE,
            'token_type': 'access_token',
        }

        return jwt.encode(
            payload=payload,
            algorithm=self._token_config.ACCESS_TOKEN_ALGORITHM,
            key=self._token_config.access_token_private_key,
        )

    def decode_access_token(self, access_token: str) -> dict[str, Any]:
        try:
            return jwt.decode(
                jtw=access_token,
                algorithms=[self._token_config.ACCESS_TOKEN_ALGORITHM,],
                key=self._token_config.access_token_public_key,
                audience=self._token_config.ACCESS_TOKEN_AUDIENCE,
            )
        except InvalidSignatureError:
            raise InvalidTokenSignatureError('Access token signature error')
        except InvalidAudienceError:
            raise InvalidTokenAudienceError('Access token audience error')
        except InvalidAlgorithmError:
            raise InvalidTokenAlgorithmError('Access token algorithm error')
        except InvalidKeyError:
            raise InvalidTokenKeyError('Access token key error')
        except DecodeError:
            raise DecodeTokenError('Access token decode error')
        except InvalidTokenError:
            raise TokenInvalidError('Access token error')

    async def encode_refresh_token(self, payload: dict[str, Any]) -> str:
        now = datetime.now(UTC)
        token_id = uuid4()
        payload = {
            **payload,
            'jti': str(token_id),
            'iat': now,
            'exp': now + timedelta(days=self._token_config.REFRESH_TOKEN_EXPIRE_DAYS),
            'aud': self._token_config.REFRESH_TOKEN_AUDIENCE,
            'version': self._token_config.REFRESH_TOKEN_VERSION,
            'token_type': 'refresh_token',
        }

        refresh_token = jwt.encode(
            payload=payload,
            algorithm=self._token_config.REFRESH_TOKEN_ALGORITHM,
            key=self._token_config.refresh_token_private_key,
        )

        user_id: UUID = payload['sub']
        issued_at: datetime = payload['iat']
        expired_at: datetime = payload['exp']
        audience = self._token_config.REFRESH_TOKEN_AUDIENCE
        await self._auth_commands.insert_refresh_token_data(
            refresh_token_id=token_id,
            user_id=user_id,
            issued_at=issued_at,
            expired_at=expired_at,
            audience=audience,
        )

        return refresh_token

    def decode_refresh_token(self, refresh_token: str) -> dict[str, Any]:
        try:
            return jwt.decode(
                jtw=refresh_token,
                algorithms=[self._token_config.REFRESH_TOKEN_ALGORITHM,],
                key=self._token_config.refresh_token_public_key,
                audience=self._token_config.REFRESH_TOKEN_AUDIENCE,
            )
        except InvalidSignatureError:
            raise InvalidTokenSignatureError('Refresh token signature error')
        except InvalidAudienceError:
            raise InvalidTokenAudienceError('Refresh token audience error')
        except InvalidAlgorithmError:
            raise InvalidTokenAlgorithmError('Refresh token algorithm error')
        except InvalidKeyError:
            raise InvalidTokenKeyError('Refresh token key error')
        except DecodeError:
            raise DecodeTokenError('Refresh token decode error')
        except InvalidTokenError:
            raise TokenInvalidError('Refresh token error')


class LoginUserCase:
    """Кейс по входу в аккаунт пользователя"""

    def __init__(self, manage_token_case: ManageTokenCase, auth_queries: AuthQueriesRepository) -> None:
        self._manage_token_case = manage_token_case
        self._auth_queries = auth_queries

    async def login_user(self, email: str, password: str) -> TokenInfoDTO:
        columns = await self._auth_queries.select_user_id_pass_role_by_email(email)
        columns = UserGuards.require_columns_exist(columns)
        verify_pass(password, columns['password_hash'])

        UserGuards.require_user_in_columns_blocked(columns)
        UserGuards.require_user_in_columns_closed(columns)

        user_id = columns['user_id']
        role = columns['role']
        access_payload = {
            'sub': str(user_id),
            'role': role,
        }
        refresh_payload = {
            'sub': str(user_id)
        }

        access_token = self._manage_token_case.encode_access_token(access_payload)
        refresh_token = await self._manage_token_case.encode_refresh_token(refresh_payload)

        return TokenInfoDTO(access_token=access_token, refresh_token=refresh_token)


class LogoutUserCase:
    """Кейс по выходу из аккаунта пользователя"""

    def __init__(self, auth_commands: AuthCommandsRepository, token_config: TokenConfig, current_user_redis_commands: CurrentUserRedisCommandsRepository) -> None:
        self._auth_commands = auth_commands
        self._token_config = token_config
        self._current_user_redis_commands = current_user_redis_commands

    async def logout_user_device(self, current_user: FullUserInfoDTO) -> None:
        await self._auth_commands.alter_user_refresh_tokens_revoked_param(current_user.user_id, self._token_config.REFRESH_TOKEN_AUDIENCE)
        await self._current_user_redis_commands.delete_current_user(current_user.user_id)

    async def logout_all_user_devices(self, current_user: FullUserInfoDTO) -> None:
        await self._auth_commands.alter_all_user_refresh_tokens_revoked_param(current_user.user_id)
        await self._current_user_redis_commands.delete_current_user(current_user.user_id)


class RefreshUserCase:
    """Кейс по обновлению токенов пользователя"""

    def __init__(self, manage_token_case: ManageTokenCase, auth_queries: AuthQueriesRepository, current_user_redis_commands: CurrentUserRedisCommandsRepository, token_config: TokenConfig, auth_commands: AuthCommandsRepository) -> None:
        self._manage_token_case = manage_token_case
        self._auth_queries = auth_queries
        self._current_user_redis_commands = current_user_redis_commands
        self._token_config = token_config
        self._auth_commands = auth_commands

    async def refresh(self, refresh_token: str) -> TokenInfoDTO:
        refresh_payload = self._manage_token_case.decode_refresh_token(refresh_token)
        user_id = refresh_payload['sub']
        version = refresh_payload['version']
        refresh_token_id = refresh_payload['jti']

        if not version == self._token_config.REFRESH_TOKEN_VERSION:
            raise InvalidTokenVersionError('Old token version')

        revoked_at = await self._auth_queries.select_refresh_token_revoked_by_id(refresh_token_id)
        if revoked_at is not None:
            raise RevokedTokenError('Token was burned before')

        user = await self._current_user_redis_commands.get_current_user(user_id)
        if user is None:
            columns = await self._auth_queries.select_user_role_by_id(user_id)
            columns = UserGuards.require_columns_exist(columns)
            UserGuards.require_user_in_columns_blocked(columns)
            UserGuards.require_user_in_columns_closed(columns)

            role = columns['role']
        else:
            UserGuards.require_user_blocked(user)
            UserGuards.require_user_closed(user)

            role = user.role

        new_access_payload = {
            'sub': str(user_id),
            'role': role
        }
        new_refresh_payload = {
            'sub': str(user_id),
        }

        new_refresh_token = await self._manage_token_case.encode_refresh_token(new_refresh_payload)
        new_access_token = self._manage_token_case.encode_access_token(new_access_payload)

        await self._auth_commands.alter_refresh_token_revoked_param(refresh_token_id)

        return TokenInfoDTO(access_token=new_access_token, refresh_token=new_refresh_token)


class ShowCurrentUserCase:
    """Кейс по показу текущего пользователя"""

    def __init__(self, manage_token_case: ManageTokenCase, auth_queries: AuthQueriesRepository, current_user_redis_commands: CurrentUserRedisCommandsRepository) -> None:
        self._manage_token_case = manage_token_case
        self._auth_queries = auth_queries
        self._current_user_redis_commands = current_user_redis_commands

    async def _current(self, token: str, admin: bool | None = None, vip: bool | None = None):
        access_payload = self._manage_token_case.decode_access_token(token)
        user_id = access_payload['sub']

        user = await self._current_user_redis_commands.get_current_user(user_id)
        if user is None:
            user = await self._auth_queries.select_user_by_id(user_id)
            user = UserGuards.require_user_exist(user)

            await self._current_user_redis_commands.set_current_user(FullUserInfoDTO.model_validate(user))

        UserGuards.require_user_blocked(user)
        UserGuards.require_user_closed(user)

        if admin is not None:
            role = access_payload['role']

            if not user.role == role and user.role == UserRoleEnum.ADMIN:
                raise ForbiddenError('User role != admin')

        if vip is not None:
            role = access_payload['role']

            if not user.role == role and user.role == UserRoleEnum.VIP:
                raise ForbiddenError('User role != vip')

        return FullUserInfoDTO.model_validate(user)

    async def current_standard(self, token: str) -> FullUserInfoDTO:
        return await self._current(token)

    async def current_admin(self, token: str) -> FullUserInfoDTO:
        return await self._current(token, admin=True)

    async def current_vip(self, token: str) -> FullUserInfoDTO:
        return await self._current(token, vip=True)
