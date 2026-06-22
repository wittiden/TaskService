import pytest

from app.common.enums.users import UserRoleEnum
from tests.factories.user import UserFactory


class TestCreteUserCase:
    """"""

    def test_create_standard_user(self):
        user = UserFactory(admin=True, block=True)

        assert user.name is not None
        assert user.email is not None
        assert user.role == UserRoleEnum.ADMIN
        assert user.blocked_at is not None
