import pytest
from fastapi import status

from tests.factories.user import UsersFactory


class TestUserAPI:
    """Тестирование апи пользователя"""

    @pytest.mark.parametrize(
        'url, is_admin, is_vip',
        [
            ('/api/v1/users/standard', False, False),
            ('/api/v1/users/admin', True, False),
            ('/api/v1/users/vip', False, True),
        ],
        ids=[
            'standard',
            'admin',
            'vip',
        ],
    )
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_user_endpoint_good(self, client, url, is_admin, is_vip):
        user = UsersFactory(admin=is_admin, vip=is_vip)
        request_data = {
            'name': user.name,
            'email': user.email,
            'password': user.password_hash,
        }

        response = await client.post(url=url, json=request_data)
        response_data = response.json()

        assert response.status_code == status.HTTP_201_CREATED
        assert response_data['name'] == request_data['name']
        assert response_data['email'] == request_data['email']
        assert 'password' not in response_data

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_update_me_endpoint_good(self, current_standard):
        user = UsersFactory()
        request_data = {
            'name': user.name,
            'email': None,
        }

        response = await current_standard.patch(
            url='/api/v1/users/me',
            json=request_data,
        )
        response_data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert response_data['name'] == request_data['name']
        assert response_data['email'] != request_data['email']

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_close_my_account_endpoint_good(self, current_standard):
        response = await current_standard.patch(url='/api/v1/users/me/close')

        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_delete_user_account_endpoint_good(self, current_admin, async_session):
        user = UsersFactory(close=True)
        async_session.add(user)
        await async_session.commit()

        delete_response = await current_admin.delete(url=f'/api/v1/admin/users/{user.user_id}')

        assert delete_response.status_code == status.HTTP_204_NO_CONTENT
