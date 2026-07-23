import pytest
from fastapi import status

from app.modules.sessions.contracts.dtos import FullRefreshTokenInfoDTO
from tests.factories.refresh_token import RefreshTokensFactory


class TestSessionAPI:
    """Тестирование апи сессий"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_show_refresh_tokens_endpoint_good(self, current_admin):
        response = await current_admin.get(url='/api/v1/admin/tokens/')

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_show_user_active_refresh_tokens_endpoint_good(
        self, current_admin, async_session
    ):
        refresh_token = RefreshTokensFactory()
        async_session.add(refresh_token)
        await async_session.commit()

        response = await current_admin.get(url=f'/api/v1/admin/tokens/{refresh_token.user_id}')

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_show_refresh_token_by_id_endpoint_good(self, current_admin, async_session):
        refresh_token = RefreshTokensFactory()
        async_session.add(refresh_token)
        await async_session.commit()

        response = await current_admin.get(
            url=f'/api/v1/admin/tokens/by-id/{refresh_token.refresh_token_id}'
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json().keys() == FullRefreshTokenInfoDTO.model_fields.keys()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_delete_refresh_token_by_id_endpoint_good(self, current_admin, async_session):
        refresh_token = RefreshTokensFactory(revoke=True)
        async_session.add(refresh_token)
        await async_session.commit()

        response = await current_admin.delete(
            url=f'/api/v1/admin/tokens/{refresh_token.refresh_token_id}'
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
