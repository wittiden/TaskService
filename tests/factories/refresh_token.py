from datetime import UTC, datetime, timedelta
from uuid import uuid4

from factory import Factory, LazyAttribute, LazyFunction, SelfAttribute, SubFactory, Trait

from app.infrastructure.database.model import RefreshTokenModel
from tests.factories.user import UsersFactory


class RefreshTokensFactory(Factory):
    """Фабрика по созданию refresh токенов"""

    class Meta:
        model = RefreshTokenModel

    user = SubFactory(UsersFactory)

    refresh_token_id = LazyFunction(uuid4)
    user_id = SelfAttribute('user.user_id')
    issued_at = LazyFunction(lambda: datetime.now(UTC))
    expired_at = LazyAttribute(lambda obj: obj.issued_at + timedelta(days=1))
    revoked_at = None
    audience = 'api'

    class Params:
        revoke = Trait(revoked_at=LazyFunction(lambda: datetime.now(UTC)))
