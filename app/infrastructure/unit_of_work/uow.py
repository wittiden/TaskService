from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession


class ProgramUnitOfWork:
    """Реализация паттерна uow для атомарности транзакций в бд"""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

    async def __aenter__(self) -> ProgramUnitOfWork:
        return self

    async def __aexit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None) -> None:
        try:
            if exc_type is not None:
                await self._async_session.rollback()

            else:
                await self._async_session.commit()
        except Exception as ex:
            await self._async_session.rollback()
            raise ex

        finally:
            await self._async_session.close()
