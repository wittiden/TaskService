import pytest
from fastapi import status

from app.modules.sessions.contracts.dtos import FullRefreshTokenInfoDTO
from tests.factories.refresh_token import RefreshTokensFactory


class TestReadSessionRouters:
    """Тестирование роутеров чтения сессий"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_show_refresh_tokens_endpoint_good(self, current_admin):
        client, _ = current_admin

        response = await client.get(url='/api/v1/admin/sessions/')

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_show_user_active_refresh_tokens_endpoint_good(
        self, current_admin, async_session
    ):
        client, _ = current_admin

        refresh_token = RefreshTokensFactory()
        async_session.add(refresh_token)
        await async_session.commit()

        response = await client.get(url=f'/api/v1/admin/sessions/{refresh_token.user_id}')

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_show_refresh_token_by_id_endpoint_good(self, current_admin, async_session):
        client, _ = current_admin

        refresh_token = RefreshTokensFactory()
        async_session.add(refresh_token)
        await async_session.commit()

        response = await client.get(
            url=f'/api/v1/admin/sessions/by-id/{refresh_token.refresh_token_id}'
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json().keys() == FullRefreshTokenInfoDTO.model_fields.keys()
