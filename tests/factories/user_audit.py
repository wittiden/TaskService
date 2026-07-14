from datetime import UTC, datetime
from uuid import uuid4

from factory import Factory, LazyFunction

from app.infrastructure.database.model import UserAuditModel


class UserAuditsFactory(Factory):
    """Фабрика по созданию аудитов пользователей"""

    class Meta:
        model = UserAuditModel

    user_audit_id = LazyFunction(uuid4)
    user_id = LazyFunction(uuid4)
    field_name = 'field'
    new_value = 'new_value'
    old_value = 'old_value'
    changed_at = LazyFunction(lambda: datetime.now(UTC))
