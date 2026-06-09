from app.common.enums.auth import TokenTypeEnum
from app.modules.auth.exceptions import InvalidTokenTypeError, TokenNotFoundError
from refresh_token import RefreshTokenModel


class AuthGuards:
    """Класс бизнес правил модуля аутентификации"""

    @staticmethod
    def require_refresh_token_type(token_type: str):
        if token_type != TokenTypeEnum.REFRESH_TOKEN:
            raise InvalidTokenTypeError('Invalid refresh token type error')

    @staticmethod
    def require_access_token_type(token_type: str):
        if token_type != TokenTypeEnum.ACCESS_TOKEN:
            raise InvalidTokenTypeError('Invalid access token type error')

    @staticmethod
    def require_refresh_token(refresh_token: RefreshTokenModel | None) -> RefreshTokenModel:
        if refresh_token is None:
            raise TokenNotFoundError('Refresh token not found error')

        return refresh_token
