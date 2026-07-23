import pytest
from fastapi import status

from app.modules.auth.contracts.dtos import TokenInfoDTO
from app.modules.users.contracts.dtos import SecurityUserInfoDTO
from tests.factories.user import UsersFactory


class TestAuthAPI:
    """Тестирование апи аутентификации"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_login_user_endpoint_good(self, client):
        user = UsersFactory()
        create_request_data = {
            'name': user.name,
            'email': user.email,
            'password': user.password_hash,
        }

        create_response = await client.post(url='/api/v1/users/standard', json=create_request_data)
        create_response_data: dict = create_response.json()

        assert create_response.status_code == status.HTTP_201_CREATED
        assert create_response_data.keys() == SecurityUserInfoDTO.model_fields.keys()

        request_data = {'email': user.email, 'password': user.password_hash}

        response = await client.post(
            url='/api/v1/auth/login',
            json=request_data,
        )
        response_data: dict = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert response_data.keys() == TokenInfoDTO.model_fields.keys()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_logout_user_device_endpoint_good(self, current_standard):
        response = await current_standard.post(url='/api/v1/auth/logout')

        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_logout_all_user_device_endpoint_good(self, current_standard):
        response = await current_standard.post(url='/api/v1/auth/logout-all')

        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_refresh_endpoint_good(self, client):
        user = UsersFactory()
        create_request_data = {
            'name': user.name,
            'email': user.email,
            'password': user.password_hash,
        }

        create_response = await client.post(url='/api/v1/users/standard', json=create_request_data)
        create_response_data: dict = create_response.json()

        assert create_response.status_code == status.HTTP_201_CREATED
        assert create_response_data.keys() == SecurityUserInfoDTO.model_fields.keys()

        request_data = {'email': user.email, 'password': user.password_hash}

        response = await client.post(
            url='/api/v1/auth/login',
            json=request_data,
        )
        response_data: dict = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert response_data.keys() == TokenInfoDTO.model_fields.keys()

        refresh_request_data = {'refresh_token': response_data['refresh_token']}
        refresh_response = await client.post(
            url='/api/v1/auth/refresh',
            json=refresh_request_data,
        )
        refresh_response_data: dict = refresh_response.json()

        assert refresh_response.status_code == status.HTTP_200_OK
        assert refresh_response_data.keys() == TokenInfoDTO.model_fields.keys()
