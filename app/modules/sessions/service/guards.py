from loguru import logger

from app.infrastructure.database.model import RefreshTokenModel
from app.modules.sessions.exceptions import RefreshTokenNotFoundError


class SessionGuards:
    """Класс бизнес правил сессий"""

    @staticmethod
    def require_refresh_token_exist(obj: RefreshTokenModel | None) -> RefreshTokenModel:
        if obj is None:
            logger.warning('Refresh token cant found - RefreshTokenNotFoundError')
            raise RefreshTokenNotFoundError('Refresh token cant found')

        return obj
