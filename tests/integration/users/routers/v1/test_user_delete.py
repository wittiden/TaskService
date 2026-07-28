import pytest
from fastapi import status

from tests.factories.user import UsersFactory


class TestDeleteUserRouters:
    """Тестирование роутеров удаления пользователей"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_delete_user_account_endpoint_good(self, current_admin, async_session):
        client, _ = current_admin

        user = UsersFactory(close=True)
        async_session.add(user)
        await async_session.commit()

        response = await client.delete(url=f'/api/v1/admin/users/{user.user_id}')

        assert response.status_code == status.HTTP_204_NO_CONTENT
