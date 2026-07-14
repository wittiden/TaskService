import pytest
from sqlalchemy.exc import IntegrityError

from app.modules.audits.exceptions import UserAuditModelIntegrityError
from tests.factories.user_audit import UserAuditsFactory


class TestCreateUserAuditCase:
    """Тестовый кейс по созданию аудитов пользователей"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_user_audit_good(
        self, mock_user_audit_commands, create_user_audit_mock_case
    ):
        user_audit = UserAuditsFactory()

        await create_user_audit_mock_case.create_user_audit(
            user_audit.user_id, user_audit.field_name, user_audit.old_value, user_audit.new_value
        )

        mock_user_audit_commands.insert_user_audit_obj.assert_awaited_once_with(
            user_audit.user_id, user_audit.field_name, user_audit.old_value, user_audit.new_value
        )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_user_audit_bad(
        self, mock_user_audit_commands, create_user_audit_mock_case
    ):
        user_audit = UserAuditsFactory()

        mock_user_audit_commands.insert_user_audit_obj.side_effect = IntegrityError(
            statement=None, params=None, orig=Exception('duplicate key')
        )

        with pytest.raises(UserAuditModelIntegrityError):
            await create_user_audit_mock_case.create_user_audit(
                user_audit.user_id,
                user_audit.field_name,
                user_audit.old_value,
                user_audit.new_value,
            )

        mock_user_audit_commands.insert_user_audit_obj.assert_awaited_once_with(
            user_audit.user_id, user_audit.field_name, user_audit.old_value, user_audit.new_value
        )
