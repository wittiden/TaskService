import asyncio

from app.common.email_service.utils import send_email
from app.common.task_service.utils import celery


@celery.task(  # type: ignore
    name='send_email',
    max_retries=3,
    default_retry_delay=60,
    time_limit=300,
    autoretry_for=(Exception,),
)
def send_email_by_celery(to_email: str, subject: str, body: str) -> None:
    asyncio.run(send_email(to_email, subject, body))
