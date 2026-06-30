from enum import StrEnum


class UserRoleEnum(StrEnum):
    """Класс для перечисления ролей пользователя"""

    STANDARD = 'standard'
    VIP = 'vip'
    ADMIN = 'admin'
