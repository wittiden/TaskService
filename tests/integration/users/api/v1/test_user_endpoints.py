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
        ids=['standard', 'admin', 'vip'],
    )
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_user_endpoint_good(self, client, url, is_vip, is_admin):
        user = UsersFactory(admin=is_admin, vip=is_vip)
        request_data = {'name': user.name, 'email': user.email, 'password': user.password_hash}

        response = await client.post(
            url=url,
            json=request_data,
        )
        response_data = response.json()

        assert response.status_code == status.HTTP_201_CREATED
        assert response_data['name'] == user.name
        assert response_data['email'] == user.email
        assert response_data['role'] == user.role
        assert 'password' not in response_data
