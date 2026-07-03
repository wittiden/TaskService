from app.infrastructure.database.model.user import UserModel
from app.modules.users.exceptions import InvalidUserDataError, UserColumnsNotFoundError, UserBlockedError, \
    UserClosedError


class UserGuards:
    """Класс бизнес правил пользователя"""

    @staticmethod
    def require_user_exist(user: UserModel | None) -> UserModel:
        if user is None:
            raise InvalidUserDataError('User cant create due to invalid data')

        return user

    @staticmethod
    def require_columns_exist(columns: dict | None) -> dict:
        if columns is None:
            raise UserColumnsNotFoundError('User columns cant found due to incorrect data')

        return columns

    @staticmethod
    def require_user_in_columns_blocked(columns: dict) -> None:
        if columns['blocked_at'] is None:
            raise UserBlockedError('User not authorize due to blocked account')

    @staticmethod
    def require_user_in_columns_closed(columns: dict) -> None:
        if columns['closed_at'] is None:
            raise UserClosedError('User not authorize due to closed account')

    @staticmethod
    def require_user_blocked(user: UserModel | None) -> None:
        if user is None:
            raise UserBlockedError('User not authorize due to blocked account')

    @staticmethod
    def require_user_closed(user: UserModel | None) -> None:
        if user is None:
            raise UserClosedError('User not authorize due to closed account')

