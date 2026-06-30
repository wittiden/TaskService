from sqlalchemy.ext.asyncio import AsyncSession


class UserQueriesRepository:
    """Репозиторий для select запросов"""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session
