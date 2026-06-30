from app.infrastructure.database.model.user import UserModel
from app.modules.users.exceptions import InvalidUserDataError


class UserGuards:
    """Класс бизнес правил пользователя"""

    @staticmethod
    def require_user_exist(user: UserModel | None) -> UserModel:
        if user is None:
            raise InvalidUserDataError('User cant create due to invalid data')

        return user
