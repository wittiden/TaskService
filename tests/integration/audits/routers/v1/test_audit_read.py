import pytest
from fastapi import status

from tests.factories.user_audit import UserAuditsFactory


class TestReadAuditRouters:
    """Тестирование роутеров чтения аудита"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_show_user_audits_endpoint_good(self, current_admin):
        client, _ = current_admin

        response = await client.get(url='/api/v1/admin/user-audits/')

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_show_user_audits_by_user_id_endpoint_good(self, current_admin, async_session):
        client, _ = current_admin

        user_audit = UserAuditsFactory()
        async_session.add(user_audit)
        await async_session.commit()

        response = await client.get(url=f'/api/v1/admin/user-audits/{user_audit.user_id}')

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_show_user_audits_by_id_endpoint_good(self, current_admin, async_session):
        client, _ = current_admin

        user_audit = UserAuditsFactory()
        async_session.add(user_audit)
        await async_session.commit()

        response = await client.get(
            url=f'/api/v1/admin/user-audits/by-id/{user_audit.user_audit_id}'
        )

        assert response.status_code == status.HTTP_200_OK
