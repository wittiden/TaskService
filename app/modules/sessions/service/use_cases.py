from uuid import UUID

from app.modules.sessions.contracts.dtos import FullRefreshTokenInfoDTO
from app.modules.sessions.exceptions import RefreshTokenNotFoundError
from app.modules.sessions.repository.commands import SessionCommandsRepository
from app.modules.sessions.repository.queries import SessionQueriesRepository
from app.modules.sessions.service.guards import SessionGuards


class ShowRefreshTokenCase:
    """Кейс по показу информации токенов"""

    def __init__(self, session_queries: SessionQueriesRepository) -> None:
        self._session_queries = session_queries

    async def show_refresh_token_by_id(self, refresh_token_id: UUID) -> FullRefreshTokenInfoDTO:
        obj = await self._session_queries.select_refresh_token_by_id(refresh_token_id)
        obj = SessionGuards.require_refresh_token_exist(obj)

        return FullRefreshTokenInfoDTO.model_validate(obj)

    async def show_user_active_refresh_tokens(
        self, user_id: UUID, offset: int = 0, limit: int = 100
    ) -> list[FullRefreshTokenInfoDTO]:
        objs = await self._session_queries.select_user_active_refresh_tokens(user_id, offset, limit)
        return [FullRefreshTokenInfoDTO.model_validate(obj) for obj in objs]

    async def show_refresh_tokens(
        self, offset: int = 0, limit: int = 100
    ) -> list[FullRefreshTokenInfoDTO]:
        objs = await self._session_queries.select_refresh_tokens(offset, limit)
        return [FullRefreshTokenInfoDTO.model_validate(obj) for obj in objs]


class DeleteRefreshTokenCase:
    """Кейс по удалению токенов"""

    def __init__(self, session_commands: SessionCommandsRepository) -> None:
        self._session_commands = session_commands

    async def delete_refresh_token_by_id(self, refresh_token_id: UUID) -> None:
        deleted_obj_id = await self._session_commands.delete_deactivate_refresh_token_by_id(
            refresh_token_id
        )
        if deleted_obj_id is None:
            raise RefreshTokenNotFoundError('Refresh token cant found for deletion')
