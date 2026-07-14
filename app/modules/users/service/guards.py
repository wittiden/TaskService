from app.infrastructure.database.model.user import UserModel
from app.modules.users.contracts.dtos import FullUserInfoDTO
from app.modules.users.exceptions import (
    InvalidUserDataError,
    UserBlockedError,
    UserClosedError,
    UserColumnsNotFoundError,
)


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
        if columns['blocked_at'] is not None:
            raise UserBlockedError('User not authorize due to blocked account')

    @staticmethod
    def require_user_in_columns_closed(columns: dict) -> None:
        if columns['closed_at'] is not None:
            raise UserClosedError('User not authorize due to closed account')

    @staticmethod
    def require_user_blocked(user: UserModel | FullUserInfoDTO) -> None:
        if user.blocked_at is not None:
            raise UserBlockedError('User not authorize due to blocked account')

    @staticmethod
    def require_user_closed(user: UserModel | FullUserInfoDTO) -> None:
        if user.closed_at is not None:
            raise UserClosedError('User not authorize due to closed account')
