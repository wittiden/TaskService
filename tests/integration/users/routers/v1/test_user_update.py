import pytest
from fastapi import status

from app.modules.users.contracts.dtos import FullUserInfoDTO, SecurityUserInfoDTO
from tests.factories.user import UsersFactory


class TestUpdateUserRouters:
    """Тестирование роутеров обновления данных пользователей"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_update_me_endpoint_good(self, current_standard):
        client, _ = current_standard

        user = UsersFactory()
        request_data = {
            'name': user.name,
            'email': None,
        }

        response = await client.patch(
            url='/api/v1/users/me',
            json=request_data,
        )
        response_data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert response_data.keys() == SecurityUserInfoDTO.model_fields.keys()
        assert response_data['name'] == request_data['name']
        assert response_data['email'] != request_data['email']

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_close_my_account_endpoint_good(self, current_standard):
        client, _ = current_standard

        response = await client.patch(url='/api/v1/users/me/close')

        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_block_user_account_endpoint_good(self, current_admin, async_session):
        client, _ = current_admin

        user = UsersFactory()
        async_session.add(user)
        await async_session.commit()

        response = await client.patch(
            url=f'/api/v1/admin/users/block/{user.user_id}',
        )
        response_data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert response_data.keys() == FullUserInfoDTO.model_fields.keys()
        assert response_data['blocked_at']

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_unblock_user_account_endpoint_good(self, current_admin, async_session):
        client, _ = current_admin

        user = UsersFactory(block=True)
        async_session.add(user)
        await async_session.commit()

        response = await client.patch(
            url=f'/api/v1/admin/users/unblock/{user.user_id}',
        )
        response_data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert response_data.keys() == FullUserInfoDTO.model_fields.keys()
        assert not response_data['blocked_at']
