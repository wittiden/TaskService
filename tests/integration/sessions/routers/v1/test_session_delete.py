import pytest
from fastapi import status

from tests.factories.refresh_token import RefreshTokensFactory


class TestDeleteSessionRouters:
    """Тестирование роутеров удаления сессий"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_delete_refresh_token_by_id_endpoint_good(self, current_admin, async_session):
        client, _ = current_admin

        refresh_token = RefreshTokensFactory(revoke=True)
        async_session.add(refresh_token)
        await async_session.commit()

        response = await client.delete(
            url=f'/api/v1/admin/sessions/{refresh_token.refresh_token_id}'
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
