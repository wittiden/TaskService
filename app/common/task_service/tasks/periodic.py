import asyncio

from app.common.task_service.utils import celery
from app.container.container import async_container
from app.modules.sessions.repository.commands import SessionCommandsRepository
from app.modules.users.repository.commands import UserCommandsRepository


@celery.task(  # type: ignore
    name='dead_tokens_delete',
    max_retries=3,
    time_limit=300,
    default_retry_delay=60,
    autoretry_for=(Exception,),
)
def daily_dead_tokens_delete() -> None:
    async def _run() -> None:
        async with async_container() as container:
            session_commands = await container.get(SessionCommandsRepository)

            await session_commands.delete_dead_tokens()

    asyncio.run(_run())


@celery.task(  # type: ignore
    name='closed_account_delete',
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    time_limit=300,
)
def daily_closed_accounts_delete() -> None:
    async def _run() -> None:
        async with async_container() as container:
            user_commands = await container.get(UserCommandsRepository)

            await user_commands.delete_closed_users()

    asyncio.run(_run())
