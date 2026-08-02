from uuid import UUID

from loguru import logger

from app.modules.sessions.contracts.dtos import FullRefreshTokenInfoDTO
from app.modules.sessions.exceptions import RefreshTokenNotFoundError
from app.modules.sessions.repository.commands import SessionCommandsRepository
from app.modules.sessions.repository.queries import SessionQueriesRepository
from app.modules.sessions.service.guards import SessionGuards


class ShowRefreshTokenCase:
    """Кейс по показу информации токенов"""

    __slots__ = ('_session_queries',)

    def __init__(self, session_queries: SessionQueriesRepository) -> None:
        self._session_queries = session_queries

    async def show_refresh_token_by_id(self, refresh_token_id: UUID) -> FullRefreshTokenInfoDTO:
        logger.debug(
            'Showing refresh token by ID', extra={'refresh_token_id': str(refresh_token_id)}
        )

        obj = await self._session_queries.select_refresh_token_by_id(refresh_token_id)
        obj = SessionGuards.require_refresh_token_exist(obj)

        logger.info(
            'Refresh token found by ID',
            extra={
                'refresh_token_id': str(refresh_token_id),
                'user_id': str(obj.user_id),
            },
        )
        return FullRefreshTokenInfoDTO.model_validate(obj)

    async def show_user_active_refresh_tokens(
        self, user_id: UUID, offset: int = 0, limit: int = 100
    ) -> list[FullRefreshTokenInfoDTO]:
        logger.debug(
            'Showing user active refresh tokens',
            extra={
                'user_id': str(user_id),
                'offset': offset,
                'limit': limit,
            },
        )

        objs = await self._session_queries.select_user_active_refresh_tokens(user_id, offset, limit)

        logger.info(
            'User active refresh tokens retrieved',
            extra={
                'user_id': str(user_id),
                'count': len(objs),
                'offset': offset,
                'limit': limit,
            },
        )
        return [FullRefreshTokenInfoDTO.model_validate(obj) for obj in objs]

    async def show_refresh_tokens(
        self, offset: int = 0, limit: int = 100
    ) -> list[FullRefreshTokenInfoDTO]:
        logger.debug(
            'Showing all refresh tokens',
            extra={
                'offset': offset,
                'limit': limit,
            },
        )

        objs = await self._session_queries.select_refresh_tokens(offset, limit)

        logger.info(
            'All refresh tokens retrieved',
            extra={
                'count': len(objs),
                'offset': offset,
                'limit': limit,
            },
        )
        return [FullRefreshTokenInfoDTO.model_validate(obj) for obj in objs]


class DeleteRefreshTokenCase:
    """Кейс по удалению токенов"""

    __slots__ = ('_session_commands',)

    def __init__(self, session_commands: SessionCommandsRepository) -> None:
        self._session_commands = session_commands

    async def delete_refresh_token_by_id(self, refresh_token_id: UUID) -> None:
        logger.debug(
            'Deleting refresh token by ID', extra={'refresh_token_id': str(refresh_token_id)}
        )

        deleted_obj_id = await self._session_commands.delete_deactivate_refresh_token_by_id(
            refresh_token_id
        )
        if deleted_obj_id is None:
            logger.warning(
                'Refresh token not found for deletion',
                extra={'refresh_token_id': str(refresh_token_id)},
            )
            raise RefreshTokenNotFoundError('Refresh token cant found for deletion')

        logger.info(
            'Refresh token deleted successfully',
            extra={
                'refresh_token_id': str(refresh_token_id),
                'deleted_obj_id': deleted_obj_id,
            },
        )
