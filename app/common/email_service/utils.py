from email.message import EmailMessage
from email.utils import formataddr

import aiosmtplib

from app.common.email_service.config import email_service_config


async def send_email(to_email: str, subject: str, body: str) -> None:
    message = EmailMessage()
    message['From'] = formataddr(('TaskService', email_service_config.SMTP_USER))
    message['To'] = to_email
    message['Subject'] = subject
    message.set_content(body)

    await aiosmtplib.send(
        message,
        hostname=email_service_config.SMTP_HOST,
        port=email_service_config.SMTP_PORT,
        username=email_service_config.SMTP_USER,
        password=email_service_config.SMTP_PASS,
        timeout=30,
        start_tls=True,
    )
