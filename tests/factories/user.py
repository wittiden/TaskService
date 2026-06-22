from datetime import datetime, UTC
from factory import Factory, LazyFunction, Faker, Trait

from app.common.enums.users import UserRoleEnum
from app.infrastructure.database.models import UserModel


class UserFactory(Factory):
    """Фабрика по созданию пользователей для тестов"""

    class Meta:
        model = UserModel

    name = Faker('name')
    email = Faker('email')
    password_hash = Faker('password')
    role = UserRoleEnum.STANDARD_USER
    created_at = LazyFunction(lambda: datetime.now(UTC))
    updated_at = None
    blocked_at = None
    closed_at = None

    class Params:
        admin = Trait(
            role = UserRoleEnum.ADMIN
        )
        vip = Trait(
            role = UserRoleEnum.VIP_USER
        )

        update = Trait(
            updated_at = LazyFunction(lambda: datetime.now(UTC))
        )
        block = Trait(
            blocked_at = LazyFunction(lambda: datetime.now(UTC))
        )
        close = Trait(
            closed_at = LazyFunction(lambda: datetime.now(UTC))
        )
