import pytest
from fastapi import status

from app.modules.users.contracts.dtos import FullUserInfoDTO, SecurityUserInfoDTO
from tests.factories.user import UsersFactory


class TestReadUserRouters:
    """Тестирование роутеров чтения пользователей"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_show_me_endpoint_good(self, current_standard):
        client, _ = current_standard

        response = await client.get(
            url='/api/v1/users/me',
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json().keys() == SecurityUserInfoDTO.model_fields.keys()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_show_user_by_id_endpoint_good(self, current_admin, async_session):
        client, _ = current_admin

        user = UsersFactory()
        async_session.add(user)
        await async_session.commit()

        response = await client.get(
            url=f'/api/v1/admin/users/{user.user_id}',
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json().keys() == FullUserInfoDTO.model_fields.keys()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_show_users_endpoint_good(self, current_admin):
        client, _ = current_admin

        response = await client.get(
            url='/api/v1/admin/users/',
        )

        assert response.status_code == status.HTTP_200_OK
