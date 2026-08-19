from email.message import EmailMessage
from email.utils import formataddr

import aiosmtplib
from aiosmtplib import SMTPException, SMTPTimeoutError
from loguru import logger

from app.common.config import application_config
from app.common.email_service.config import email_service_config
from app.common.email_service.exception import SendEmailError, TimeoutEmailError


async def send_email(to_email: str, subject: str, body: str) -> None:
    if application_config.is_test:
        return

    envelope = EmailMessage()
    envelope['From'] = formataddr(('TaskService', email_service_config.SMTP_USER))
    envelope['To'] = to_email
    envelope['Subject'] = subject
    envelope.add_alternative(body, subtype='html')

    try:
        await aiosmtplib.send(
            envelope,
            hostname=email_service_config.SMTP_HOST,
            port=email_service_config.SMTP_PORT,
            username=email_service_config.SMTP_USER,
            password=email_service_config.SMTP_PASS,
            start_tls=True,
            timeout=30,
        )
    except SMTPTimeoutError as exc:
        logger.error(f'Failed to send email {exc}')
        raise TimeoutEmailError(str(exc)) from exc
    except SMTPException as exc:
        logger.error(f'Failed to send due to timeout email {exc}')
        raise SendEmailError(str(exc)) from exc
