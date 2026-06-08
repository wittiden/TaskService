from enum import StrEnum


class UserRoleEnum(StrEnum):
    """Класс для перечисления ролей пользователя"""

    UNKNOWN_USER = 'unknown_user'
    STANDARD_USER = 'standard_user'
    VIP_USER = 'vip_user'
    ADMIN = 'admin'
