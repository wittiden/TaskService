import pytest

from app.modules.sessions.exceptions import RefreshTokenNotFoundError
from tests.factories.refresh_token import RefreshTokensFactory


class TestDeleteRefreshTokenCase:
    """Тестовый кейс по удалению refresh токенов"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_refresh_token_by_id_good(
        self, mock_session_commands, delete_refresh_token_mock_case
    ):
        refresh_token = RefreshTokensFactory.build(revoke=True)

        mock_session_commands.delete_deactivate_refresh_token_by_id.return_value = (
            refresh_token.refresh_token_id
        )

        await delete_refresh_token_mock_case.delete_refresh_token_by_id(
            refresh_token.refresh_token_id
        )

        mock_session_commands.delete_deactivate_refresh_token_by_id.assert_awaited_once_with(
            refresh_token.refresh_token_id
        )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_refresh_token_by_id_bad(
        self, mock_session_commands, delete_refresh_token_mock_case
    ):
        refresh_token = RefreshTokensFactory.build()

        mock_session_commands.delete_deactivate_refresh_token_by_id.return_value = None

        with pytest.raises(RefreshTokenNotFoundError):
            await delete_refresh_token_mock_case.delete_refresh_token_by_id(
                refresh_token.refresh_token_id
            )

        mock_session_commands.delete_deactivate_refresh_token_by_id.assert_awaited_once_with(
            refresh_token.refresh_token_id
        )
