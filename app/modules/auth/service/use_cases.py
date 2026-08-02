from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

import jwt
from jwt import (
    DecodeError,
    InvalidAlgorithmError,
    InvalidAudienceError,
    InvalidKeyError,
    InvalidSignatureError,
    InvalidTokenError,
)
from loguru import logger

from app.common.enums.user import UserRoleEnum
from app.common.security.pass_utils import verify_pass
from app.infrastructure.redis.repositories.current_user.commands import (
    CurrentUserRedisCommandsRepository,
)
from app.modules.auth.contracts.dtos import TokenInfoDTO
from app.modules.auth.exceptions import (
    DecodeTokenError,
    ForbiddenError,
    InvalidTokenAlgorithmError,
    InvalidTokenAudienceError,
    InvalidTokenKeyError,
    InvalidTokenSignatureError,
    InvalidTokenVersionError,
    RevokedTokenError,
    TokenInvalidError,
)
from app.modules.auth.jwt_config import TokenConfig
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
                jwt=access_token,
                algorithms=[
                    self._token_config.ACCESS_TOKEN_ALGORITHM,
                ],
                key=self._token_config.access_token_public_key,
                audience=self._token_config.ACCESS_TOKEN_AUDIENCE,
            )
        except InvalidSignatureError as exc:
            raise InvalidTokenSignatureError(str(exc)) from exc
        except InvalidAudienceError as exc:
            raise InvalidTokenAudienceError(str(exc)) from exc
        except InvalidAlgorithmError as exc:
            raise InvalidTokenAlgorithmError(str(exc)) from exc
        except InvalidKeyError as exc:
            raise InvalidTokenKeyError(str(exc)) from exc
        except DecodeError as exc:
            raise DecodeTokenError(str(exc)) from exc
        except InvalidTokenError as exc:
            raise TokenInvalidError(str(exc)) from exc

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
                jwt=refresh_token,
                algorithms=[
                    self._token_config.REFRESH_TOKEN_ALGORITHM,
                ],
                key=self._token_config.refresh_token_public_key,
                audience=self._token_config.REFRESH_TOKEN_AUDIENCE,
            )
        except InvalidSignatureError as exc:
            raise InvalidTokenSignatureError(str(exc)) from exc
        except InvalidAudienceError as exc:
            raise InvalidTokenAudienceError(str(exc)) from exc
        except InvalidAlgorithmError as exc:
            raise InvalidTokenAlgorithmError(str(exc)) from exc
        except InvalidKeyError as exc:
            raise InvalidTokenKeyError(str(exc)) from exc
        except DecodeError as exc:
            raise DecodeTokenError(str(exc)) from exc
        except InvalidTokenError as exc:
            raise TokenInvalidError(str(exc)) from exc


class LoginUserCase:
    """Кейс по входу в аккаунт пользователя"""

    __slots__ = ('_auth_queries', '_manage_token_case')

    def __init__(
        self, manage_token_case: ManageTokenCase, auth_queries: AuthQueriesRepository
    ) -> None:
        self._manage_token_case = manage_token_case
        self._auth_queries = auth_queries

    async def login_user(self, email: str, password: str) -> TokenInfoDTO:
        logger.debug('User login attempt', extra={'email': email})

        columns = await self._auth_queries.select_user_id_pass_role_by_email(email)
        columns = UserGuards.require_columns_exist(columns)
        UserGuards.require_user_in_columns_closed(columns)
        UserGuards.require_user_in_columns_blocked(columns)

        verify_pass(password, columns['password_hash'])

        user_id = columns['user_id']
        role = columns['role']

        logger.debug(
            'Password verified successfully', extra={'user_id': str(user_id), 'email': email}
        )

        access_payload = {
            'sub': str(user_id),
            'role': role,
        }
        refresh_payload = {'sub': str(user_id)}

        access_token = self._manage_token_case.encode_access_token(access_payload)
        refresh_token = await self._manage_token_case.encode_refresh_token(refresh_payload)

        logger.info(
            'User logged in successfully',
            extra={
                'user_id': str(user_id),
                'email': email,
                'role': role,
            },
        )
        return TokenInfoDTO(access_token=access_token, refresh_token=refresh_token)


class LogoutUserCase:
    """Кейс по выходу из аккаунта пользователя"""

    __slots__ = ('_auth_commands', '_current_user_redis_commands', '_token_config')

    def __init__(
        self,
        auth_commands: AuthCommandsRepository,
        token_config: TokenConfig,
        current_user_redis_commands: CurrentUserRedisCommandsRepository,
    ) -> None:
        self._auth_commands = auth_commands
        self._token_config = token_config
        self._current_user_redis_commands = current_user_redis_commands

    async def logout_user_device(self, current_user: FullUserInfoDTO) -> None:
        logger.debug(
            'Logout from device',
            extra={
                'user_id': str(current_user.user_id),
                'email': current_user.email,
            },
        )

        await self._auth_commands.alter_user_refresh_tokens_revoked_param(
            current_user.user_id, self._token_config.REFRESH_TOKEN_AUDIENCE
        )
        await self._current_user_redis_commands.delete_current_user(current_user.user_id)
        logger.info(
            'User logged out from device',
            extra={
                'user_id': str(current_user.user_id),
                'email': current_user.email,
            },
        )

    async def logout_all_user_devices(self, current_user: FullUserInfoDTO) -> None:
        logger.debug(
            'Logout from all devices',
            extra={
                'user_id': str(current_user.user_id),
                'email': current_user.email,
            },
        )

        await self._auth_commands.alter_all_user_refresh_tokens_revoked_param(current_user.user_id)
        await self._current_user_redis_commands.delete_current_user(current_user.user_id)

        logger.info(
            'User logged out from all devices',
            extra={
                'user_id': str(current_user.user_id),
                'email': current_user.email,
            },
        )

    async def logout_all_user_devices_by_id(self, user_id: UUID) -> None:
        logger.debug('Logout from all devices by user ID', extra={'user_id': str(user_id)})

        await self._auth_commands.alter_all_user_refresh_tokens_revoked_param(user_id)
        await self._current_user_redis_commands.delete_current_user(user_id)

        logger.info('User logged out from all devices by ID', extra={'user_id': str(user_id)})


class RefreshUserCase:
    """Кейс по обновлению токенов пользователя"""

    __slots__ = (
        '_auth_commands',
        '_auth_queries',
        '_current_user_redis_commands',
        '_manage_token_case',
        '_token_config',
    )

    def __init__(
        self,
        manage_token_case: ManageTokenCase,
        auth_queries: AuthQueriesRepository,
        current_user_redis_commands: CurrentUserRedisCommandsRepository,
        token_config: TokenConfig,
        auth_commands: AuthCommandsRepository,
    ) -> None:
        self._manage_token_case = manage_token_case
        self._auth_queries = auth_queries
        self._current_user_redis_commands = current_user_redis_commands
        self._token_config = token_config
        self._auth_commands = auth_commands

    async def refresh(self, refresh_token: str) -> TokenInfoDTO:
        logger.debug('Token refresh attempt', extra={'token_preview': f'{refresh_token[:10]}...'})

        refresh_payload = self._manage_token_case.decode_refresh_token(refresh_token)
        user_id = refresh_payload['sub']
        version = refresh_payload['version']
        refresh_token_id = refresh_payload['jti']

        logger.debug(
            'Refresh token decoded',
            extra={
                'user_id': str(user_id),
                'version': version,
                'refresh_token_id': str(refresh_token_id),
            },
        )

        if version != self._token_config.REFRESH_TOKEN_VERSION:
            logger.warning(
                'Invalid token version',
                extra={
                    'user_id': str(user_id),
                    'version': version,
                    'expected_version': self._token_config.REFRESH_TOKEN_VERSION,
                },
            )
            raise InvalidTokenVersionError('Old token version')

        revoked_at = await self._auth_queries.select_refresh_token_revoked_by_id(refresh_token_id)
        if revoked_at is not None:
            logger.warning(
                'Token already revoked',
                extra={
                    'user_id': str(user_id),
                    'refresh_token_id': str(refresh_token_id),
                    'revoked_at': str(revoked_at),
                },
            )
            raise RevokedTokenError('Token was burned before')

        user = await self._current_user_redis_commands.get_current_user(user_id)
        if user is None:
            logger.debug(
                'User not found in cache, fetching from DB', extra={'user_id': str(user_id)}
            )

            columns = await self._auth_queries.select_user_role_by_id(user_id)
            columns = UserGuards.require_columns_exist(columns)
            UserGuards.require_user_in_columns_closed(columns)
            UserGuards.require_user_in_columns_blocked(columns)

            role = columns['role']

            logger.debug('User fetched from DB', extra={'user_id': str(user_id), 'role': role})
        else:
            UserGuards.require_user_closed(user)
            UserGuards.require_user_blocked(user)

            role = user.role

        new_access_payload = {'sub': str(user_id), 'role': role}
        new_refresh_payload = {
            'sub': str(user_id),
        }

        new_refresh_token = await self._manage_token_case.encode_refresh_token(new_refresh_payload)
        new_access_token = self._manage_token_case.encode_access_token(new_access_payload)

        await self._auth_commands.alter_refresh_token_revoked_param(refresh_token_id)

        logger.info(
            'Tokens refreshed successfully',
            extra={
                'user_id': str(user_id),
                'role': role,
                'old_refresh_token_id': str(refresh_token_id),
            },
        )
        return TokenInfoDTO(access_token=new_access_token, refresh_token=new_refresh_token)


class ShowCurrentUserCase:
    """Кейс по показу текущего пользователя"""

    __slots__ = ('_auth_queries', '_current_user_redis_commands', '_manage_token_case')

    def __init__(
        self,
        manage_token_case: ManageTokenCase,
        auth_queries: AuthQueriesRepository,
        current_user_redis_commands: CurrentUserRedisCommandsRepository,
    ) -> None:
        self._manage_token_case = manage_token_case
        self._auth_queries = auth_queries
        self._current_user_redis_commands = current_user_redis_commands

    async def _current(self, token: str, admin: bool | None = None, vip: bool | None = None):
        logger.debug(
            'Showing current user',
            extra={
                'token_preview': f'{token[:10]}...',
            },
        )

        access_payload = self._manage_token_case.decode_access_token(token)
        user_id = access_payload['sub']

        result = await self._auth_queries.select_not_revoked_tokens_by_user_id(user_id)
        if not result:
            logger.warning('All tokens revoked', extra={'user_id': str(user_id)})
            raise RevokedTokenError('All tokens were burned before')

        user = await self._current_user_redis_commands.get_current_user(user_id)
        if user is None:
            logger.debug(
                'User not found in cache, fetching from DB', extra={'user_id': str(user_id)}
            )

            user = await self._auth_queries.select_user_by_id(user_id)
            user = UserGuards.require_user_exist(user)

            await self._current_user_redis_commands.set_current_user(
                FullUserInfoDTO.model_validate(user)
            )

        UserGuards.require_user_closed(user)
        UserGuards.require_user_blocked(user)

        if admin is not None:
            role = access_payload['role']

            if user.role == role and user.role != UserRoleEnum.ADMIN:
                logger.warning(
                    'Forbidden: user is not admin',
                    extra={
                        'user_id': str(user_id),
                        'user_role': user.role,
                        'required_role': 'admin',
                    },
                )
                raise ForbiddenError('User role != admin')

        if vip is not None:
            role = access_payload['role']

            if user.role == role and user.role != UserRoleEnum.VIP:
                logger.warning(
                    'Forbidden: user is not VIP',
                    extra={
                        'user_id': str(user_id),
                        'user_role': user.role,
                        'required_role': 'vip',
                    },
                )
                raise ForbiddenError('User role != vip')

        logger.info(
            'Current user retrieved successfully',
            extra={
                'user_id': str(user_id),
                'email': user.email,
                'role': user.role,
                'from_cache': user is not None,
            },
        )
        return FullUserInfoDTO.model_validate(user)

    async def current_standard(self, token: str) -> FullUserInfoDTO:
        return await self._current(token)

    async def current_admin(self, token: str) -> FullUserInfoDTO:
        return await self._current(token, admin=True)

    async def current_vip(self, token: str) -> FullUserInfoDTO:
        return await self._current(token, vip=True)
