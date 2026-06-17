from app.infrastructure.database.models import UserModel
from app.modules.users.contracts.dtos import UserInfoDTO
from app.modules.users.exceptions import UserNotFoundError, BlockedUserError, ClosedUserError, ColumnsNotFoundError


class UserGuards:
    """Класс для хранения бизнес правил пользователей"""

    @staticmethod
    def require_user_is_exist(user: UserModel | None) -> UserModel:
        if user is None:
            raise UserNotFoundError('User not found error')

        return user

    @staticmethod
    def require_columns_is_exist(columns: dict | None) -> dict:
        if columns is None:
            raise ColumnsNotFoundError('Columns not found error')

        return columns

    @staticmethod
    def require_user_is_blocked(user: UserInfoDTO | UserModel) -> None:
        if user.blocked_at is not None:
            raise BlockedUserError('Blocked user error')

    @staticmethod
    def require_user_is_closed(user: UserInfoDTO | UserModel) -> None:
        if user.closed_at is not None:
            raise ClosedUserError('Closed user error')
