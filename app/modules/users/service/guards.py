from app.infrastructure.database.models import UserModel
from app.modules.users.exceptions import UserNotFoundError


class UserGuards:
    """Класс для хранения бизнес правил пользователей"""

    @staticmethod
    def require_user_is_exist(user: UserModel | None) -> UserModel:
        if user is None:
            raise UserNotFoundError('User not found error')

        return user
