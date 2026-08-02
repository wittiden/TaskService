from copy import copy
from uuid import UUID

from loguru import logger
from sqlalchemy.exc import IntegrityError

from app.common.enums.user import UserRoleEnum
from app.common.security.pass_utils import hash_pass
from app.infrastructure.redis.repositories.current_user.commands import (
    CurrentUserRedisCommandsRepository,
)
from app.modules.audits.service.use_cases import CreateUserAuditCase
from app.modules.auth.service.use_cases import LogoutUserCase
from app.modules.users.contracts.dtos import FullUserInfoDTO, SecurityUserInfoDTO
from app.modules.users.exceptions import (
    InvalidUserDataError,
    UserAlreadyBlockedError,
    UserAlreadyUnblockedError,
    UserEmailExistError,
    UserNotFoundError,
)
from app.modules.users.repository.commands import UserCommandsRepository
from app.modules.users.repository.queries import UserQueriesRepository
from app.modules.users.service.guards import UserGuards


class CreateUserCase:
    """Кейс по созданию пользователя"""

    __slots__ = ('_user_commands',)

    def __init__(self, user_commands: UserCommandsRepository) -> None:
        self._user_commands = user_commands

    async def _create(
        self, name: str, email: str, password: str, role: UserRoleEnum
    ) -> SecurityUserInfoDTO:
        logger.debug('Creating user', extra={'name': name, 'email': email, 'role': role})

        password_hash = hash_pass(password)

        try:
            user = await self._user_commands.insert_user_data(name, email, password_hash, role)
        except IntegrityError as exc:
            logger.warning(
                'Fail creating user - IntegrityError', extra={'email': email, 'exc': str(exc)}
            )
            raise InvalidUserDataError(str(exc)) from exc
        user = UserGuards.require_user_exist(user)

        logger.info(
            'Create user success',
            extra={'user_id': user.user_id, 'email': user.email, 'role': user.role},
        )
        return SecurityUserInfoDTO.model_validate(user)

    async def create_standard(self, name: str, email: str, password: str) -> SecurityUserInfoDTO:
        return await self._create(name, email, password, UserRoleEnum.STANDARD)

    async def create_vip(self, name: str, email: str, password: str) -> SecurityUserInfoDTO:
        return await self._create(name, email, password, UserRoleEnum.VIP)

    async def create_admin(self, name: str, email: str, password: str) -> SecurityUserInfoDTO:
        return await self._create(name, email, password, UserRoleEnum.ADMIN)


class UpdateUserCase:
    """Кейс по обновлению информации пользователя"""

    __slots__ = ('_create_user_audit_case', '_current_user_redis_commands', '_user_commands')

    def __init__(
        self,
        user_commands: UserCommandsRepository,
        current_user_redis_commands: CurrentUserRedisCommandsRepository,
        create_user_audit_case: CreateUserAuditCase,
    ) -> None:
        self._user_commands = user_commands
        self._current_user_redis_commands = current_user_redis_commands
        self._create_user_audit_case = create_user_audit_case

    async def update_user_params(
        self, current_user: FullUserInfoDTO, new_params: dict | None
    ) -> SecurityUserInfoDTO:
        logger.debug(
            'Updating user parameters',
            extra={
                'user_id': current_user.user_id,
                'email': current_user.email,
                'new_params': new_params,
            },
        )

        if not new_params:
            logger.debug('No new parameters to update', extra={'user_id': current_user.user_id})
            return SecurityUserInfoDTO.model_validate(current_user)

        for key, value in copy(new_params.items()):
            if key == 'password':
                continue

            if getattr(current_user, key, None) == value:
                new_params.pop(key)
                logger.debug(
                    'Parameter unchanged, skipping',
                    extra={'user_id': current_user.user_id, 'key': key},
                )

        if not new_params:
            logger.debug('All parameters unchanged', extra={'user_id': current_user.user_id})
            return SecurityUserInfoDTO.model_validate(current_user)

        if 'password' in new_params:
            password = new_params['password']
            password_hash = hash_pass(password)

            new_params.pop('password')
            new_params['password_hash'] = password_hash

            logger.debug('Password hash generated', extra={'user_id': current_user.user_id})

        try:
            user = await self._user_commands.alter_user_params(current_user.user_id, new_params)
        except IntegrityError as exc:
            logger.warning(
                'User update failed - email conflict',
                extra={
                    'user_id': current_user.user_id,
                    'email': current_user.email,
                    'error': str(exc),
                },
            )
            raise UserEmailExistError(str(exc)) from exc
        user = UserGuards.require_user_exist(user)

        await self._current_user_redis_commands.set_current_user(
            FullUserInfoDTO.model_validate(user)
        )
        logger.debug('User cache updated in Redis', extra={'user_id': current_user.user_id})

        for key, value in new_params.items():
            if 'password_hash' in key:
                await self._create_user_audit_case.create_user_audit(
                    current_user.user_id, str(key), '*****', '*****'
                )
            else:
                await self._create_user_audit_case.create_user_audit(
                    current_user.user_id,
                    str(key),
                    str(getattr(current_user, key)),
                    str(value),
                )

        logger.debug(
            'Audit entries created',
            extra={'user_id': current_user.user_id, 'fields_updated': list(new_params.keys())},
        )

        logger.info(
            'User updated successfully',
            extra={
                'user_id': user.user_id,
                'email': user.email,
                'role': user.role,
                'fields_updated': list(new_params.keys()),
            },
        )

        return SecurityUserInfoDTO.model_validate(user)


class DeleteUserCase:
    """Кейс по удалению пользователя"""

    __slots__ = ('_create_user_audit_case', '_logout_user_case', '_user_commands')

    def __init__(
        self,
        user_commands: UserCommandsRepository,
        logout_user_case: LogoutUserCase,
        create_user_audit_case: CreateUserAuditCase,
    ) -> None:
        self._user_commands = user_commands
        self._logout_user_case = logout_user_case
        self._create_user_audit_case = create_user_audit_case

    async def close_my_account(self, current_user: FullUserInfoDTO) -> None:
        logger.debug(
            'Closing user account',
            extra={
                'user_id': current_user.user_id,
                'email': current_user.email,
                'role': current_user.role,
            },
        )

        result = await self._user_commands.alter_user_closed_param(current_user.user_id)
        if result is None:
            logger.warning(
                'User not found for closing account', extra={'user_id': current_user.user_id}
            )
            raise UserNotFoundError('User with spec parameters not found for close')
        await self._logout_user_case.logout_all_user_devices(current_user)
        logger.debug('User logged out from all devices', extra={'user_id': current_user.user_id})

        await self._create_user_audit_case.create_user_audit(
            current_user.user_id, 'closed_at', None, str(result)
        )
        logger.debug(
            'Audit entry created for account closure', extra={'user_id': current_user.user_id}
        )

        logger.info(
            'User account closed successfully',
            extra={
                'user_id': current_user.user_id,
                'email': current_user.email,
                'closed_at': result,
            },
        )

    async def delete_user_account(self, user_id: UUID) -> None:
        logger.debug('Deleting user account', extra={'user_id': str(user_id)})

        deleted_obj_id = await self._user_commands.delete_closed_user_by_id(user_id)
        if deleted_obj_id is None:
            logger.warning('User not found for deletion', extra={'user_id': str(user_id)})
            raise UserNotFoundError('User with spec parameters not found for deletion')

        await self._logout_user_case.logout_all_user_devices_by_id(user_id)
        logger.debug('User logged out from all devices', extra={'user_id': str(user_id)})

        logger.info(
            'User account deleted successfully',
            extra={
                'user_id': str(user_id),
                'deleted_obj_id': deleted_obj_id,
            },
        )


class ManageUserCase:
    """Кейс по менедженгу пользователей"""

    __slots__ = ('_create_user_audit_case', '_logout_user_case', '_user_commands', '_user_queries')

    def __init__(
        self,
        user_commands: UserCommandsRepository,
        logout_user_case: LogoutUserCase,
        user_queries: UserQueriesRepository,
        create_user_audit_case: CreateUserAuditCase,
    ) -> None:
        self._user_commands = user_commands
        self._logout_user_case = logout_user_case
        self._user_queries = user_queries
        self._create_user_audit_case = create_user_audit_case

    async def block_user(self, user_id: UUID) -> FullUserInfoDTO:
        logger.debug('Blocking user', extra={'user_id': str(user_id)})

        blocked_at = await self._user_queries.select_user_block_param(user_id)
        if blocked_at:
            logger.warning(
                'User already blocked',
                extra={'user_id': str(user_id), 'blocked_at': str(blocked_at)},
            )
            raise UserAlreadyBlockedError('User account blocked before')

        user = await self._user_commands.alter_block_user_by_id(user_id)
        user = UserGuards.require_user_exist(user)
        logger.debug(
            'User blocked in database',
            extra={'user_id': str(user_id), 'blocked_at': str(user.blocked_at)},
        )

        await self._logout_user_case.logout_all_user_devices_by_id(user_id)
        logger.debug('User logged out from all devices', extra={'user_id': str(user_id)})

        await self._create_user_audit_case.create_user_audit(
            user_id, 'blocked_at', None, str(user.blocked_at)
        )
        logger.debug('Audit entry created for block', extra={'user_id': str(user_id)})

        logger.info(
            'User blocked successfully',
            extra={
                'user_id': str(user_id),
                'email': user.email,
                'role': user.role,
                'blocked_at': str(user.blocked_at),
            },
        )

        return FullUserInfoDTO.model_validate(user)

    async def unblock_user(self, user_id: UUID) -> FullUserInfoDTO:
        logger.debug('Unblocking user', extra={'user_id': str(user_id)})

        blocked_at = await self._user_queries.select_user_block_param(user_id)
        if blocked_at is None:
            logger.warning('User already unblocked', extra={'user_id': str(user_id)})
            raise UserAlreadyUnblockedError('User account unblocked before')

        user = await self._user_commands.alter_unblock_user_by_id(user_id)
        user = UserGuards.require_user_exist(user)
        logger.debug('User unblocked in database', extra={'user_id': str(user_id)})

        await self._create_user_audit_case.create_user_audit(
            user_id, 'blocked_at', str(blocked_at), None
        )
        logger.debug('Audit entry created for unblock', extra={'user_id': str(user_id)})

        logger.info(
            'User unblocked successfully',
            extra={
                'user_id': str(user_id),
                'email': user.email,
                'role': user.role,
            },
        )
        return FullUserInfoDTO.model_validate(user)


class ShowUserCase:
    """Кейс по показу информации пользователей"""

    __slots__ = ('_user_queries',)

    def __init__(self, user_queries: UserQueriesRepository) -> None:
        self._user_queries = user_queries

    async def show_me(self, current_user: FullUserInfoDTO) -> SecurityUserInfoDTO:
        logger.debug(
            'Showing current user info',
            extra={
                'user_id': current_user.user_id,
                'email': current_user.email,
                'role': current_user.role,
            },
        )

        logger.info(
            'Current user info retrieved',
            extra={
                'user_id': current_user.user_id,
                'email': current_user.email,
            },
        )
        return SecurityUserInfoDTO.model_validate(current_user)

    async def show_user_by_id(self, user_id: UUID) -> FullUserInfoDTO:
        logger.debug('Showing user by ID', extra={'user_id': str(user_id)})

        user = await self._user_queries.select_user_by_id(user_id)
        user = UserGuards.require_user_exist(user)

        logger.info(
            'User found by ID',
            extra={
                'user_id': str(user_id),
                'email': user.email,
                'role': user.role,
            },
        )
        return FullUserInfoDTO.model_validate(user)

    async def show_users(self, offset: int = 0, limit: int = 100) -> list[FullUserInfoDTO]:
        logger.debug(
            'Showing users list',
            extra={
                'offset': offset,
                'limit': limit,
            },
        )

        users = await self._user_queries.select_users(offset, limit)
        logger.info(
            'Users list retrieved',
            extra={
                'count': len(users),
                'offset': offset,
                'limit': limit,
            },
        )

        return [FullUserInfoDTO.model_validate(user) for user in users]
