from sqlalchemy.ext.asyncio import AsyncSession


class SessionCommandsRepository:
    """Репозиторий для insert, alter, delete запросов"""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session
