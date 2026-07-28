from datetime import UTC, datetime
from uuid import uuid4

from factory import Factory, LazyFunction, SelfAttribute, SubFactory

from app.infrastructure.database.model import TaskAuditModel
from tests.factories.task import TasksFactory


class TaskAuditsFactory(Factory):
    """Фабрика по созданию аудитов пользователей"""

    class Meta:
        model = TaskAuditModel

    task = SubFactory(TasksFactory)

    task_audit_id = LazyFunction(uuid4)
    task_id = SelfAttribute('task.task_id')
    field_name = 'field_name'
    new_value = 'new_value'
    old_value = 'old_value'
    changed_at = LazyFunction(lambda: datetime.now(UTC))
