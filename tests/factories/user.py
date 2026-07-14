from datetime import UTC, datetime
from uuid import uuid4

from factory import Factory, Faker, LazyFunction, Trait

from app.common.enums.user import UserRoleEnum
from app.infrastructure.database.model import UserModel


class UsersFactory(Factory):
    """Фабрика по созданию пользователей"""

    class Meta:
        model = UserModel

    user_id = LazyFunction(uuid4)
    name = Faker('name')
    email = Faker('email')
    password_hash = Faker('password')
    role = UserRoleEnum.STANDARD
    created_at = LazyFunction(lambda: datetime.now(UTC))
    blocked_at = None
    closed_at = None
    updated_at = None

    class Params:
        block = Trait(blocked_at=LazyFunction(lambda: datetime.now(UTC)))
        close = Trait(closed_at=LazyFunction(lambda: datetime.now(UTC)))
        update = Trait(updated_at=LazyFunction(lambda: datetime.now(UTC)))

        admin = Trait(role=UserRoleEnum.ADMIN)
        vip = Trait(role=UserRoleEnum.VIP)
