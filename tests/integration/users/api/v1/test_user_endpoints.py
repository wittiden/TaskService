import pytest
from fastapi import status
from httpx import AsyncClient

from tests.factories.user import UsersFactory


class TestUserAPI:
    """Класс для тестирования апи пользователя"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_standard_user_endpoint(self, client: AsyncClient):
        user = UsersFactory.build()
        user_data = {
            'name': user.name,
            'email': user.email,
            'password': user.password_hash,
        }

        response = await client.post('/api/v1/users/standard', json=user_data)

        data = response.json()

        assert response.status_code == status.HTTP_201_CREATED
        assert data['name'] == user.name
        assert data['email'] == user.email
