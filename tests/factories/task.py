from datetime import UTC, datetime
from uuid import uuid4

from factory import Factory, Faker, LazyFunction, SelfAttribute, SubFactory, Trait

from app.common.enums.task import TaskImportantLevelEnum, TaskScheduleEnum
from app.infrastructure.database.model import TaskModel
from tests.factories.user import UsersFactory


class TasksFactory(Factory):
    """Фабрика по созданию задач"""

    class Meta:
        model = TaskModel

    user = SubFactory(UsersFactory)

    task_id = LazyFunction(uuid4)
    user_id = SelfAttribute('user.user_id')
    created_at = LazyFunction(lambda: datetime.now(UTC))
    closed_at = None
    updated_at = None
    completed_at = None
    important_level = TaskImportantLevelEnum.TRIVIAL
    schedule_type = TaskScheduleEnum.DAILY
    title = Faker('text')
    description = Faker('sentence')

    class Params:
        close = Trait(closed_at=LazyFunction(lambda: datetime.now(UTC)))
        update = Trait(updated_at=LazyFunction(lambda: datetime.now(UTC)))
        complete = Trait(completed_at=LazyFunction(lambda: datetime.now(UTC)))
