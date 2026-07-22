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

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_update_user_endpoint_good(self, current_standard):
        user = UsersFactory()
        new_request_data = {
            'name': user.name,
            'email': None,
        }

        response = await current_standard.patch('/api/v1/users/me', json=new_request_data)
        response_data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert response_data['name'] == user.name
        assert response_data['email'] != user.email

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_close_my_account_endpoint_good(self, current_standard):
        user = UsersFactory(close=True)
        request_data = {
            'name': user.name,
            'email': user.email,
            'password': user.password_hash,
        }
        response = await current_standard.post(
            '/api/v1/users/standard',
            json=request_data,
        )
        print(response.status_code)
        # assert response.status_code == status.HTTP_201_CREATED

        close_response = await current_standard.patch(
            '/api/v1/users/me/close',
        )
        print(close_response.status_code)

        assert close_response.status_code == status.HTTP_204_NO_CONTENT

        # response = await current_standard.patch(
        #     '/api/v1/users/me/close',
        # )
        #
        # assert response.status_code == status.HTTP_204_NO_CONTENT

    # @pytest.mark.integration
    # @pytest.mark.asyncio
    # async def test_delete_user_account_endpoint_good(self, client, current_admin):
    #     admin_client = current_admin
    #
    #     # 1. Создаём пользователя
    #     user = UsersFactory()
    #     request_data = {
    #         'name': user.name,
    #         'email': user.email,
    #         'password': user.password_hash
    #     }
    #
    #     response = await admin_client.post(
    #         '/api/v1/users/standard',
    #         json=request_data
    #     )
    #     assert response.status_code == 201, "User creation failed"
    #     response_data = response.json()
    #     user_id = response_data['user_id']
    #     print(f"✅ User created: {user_id}")
    #
    #     # 2. Проверяем, что пользователь существует
    #     get_response = await admin_client.get(f'/api/v1/users/{user_id}')
    #     print(f"GET status: {get_response.status_code}")
    #     print(f"GET response: {get_response.json()}")
    #
    #     # 3. Удаляем
    #     delete_response = await admin_client.delete(
    #         f'/api/v1/admin/users/{user_id}',
    #     )
    #     print(f"DELETE status: {delete_response.status_code}")
    #     print(f"DELETE response: {delete_response.json()}")
    #
    #     assert delete_response.status_code == 204
