import sys

from loguru import logger

from app.common.config import application_config


def setup_logger() -> None:
    logger.remove()

    if application_config.is_test:
        return

    logger.add(sys.stdout, format='{time} | {level} | {message}', level='DEBUG')

    logger.add(
        'logs/app.json',
        format='{time} | {level} | {message}',
        rotation='500 MB',
        retention='15 days',
        serialize=True,
        level='INFO',
    )

    logger.add(
        'logs/app.log',
        level='INFO',
        format='{time} | {level} | {message}',
        rotation='500 MB',
        retention='15 days',
    )
