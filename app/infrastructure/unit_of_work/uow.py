from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession


class UnitOfWork:
    """Реализация паттерна по контролю за транзакциями на уровне приложения"""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

    async def __aenter__(self) -> UnitOfWork:
        return self

    async def __aexit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None):
        try:
            if exc_type:
                await self._async_session.rollback()
                raise

            else:
                await self._async_session.commit()
        except Exception as exc:
            await self._async_session.rollback()
            raise exc
        finally:
            await self._async_session.close()
