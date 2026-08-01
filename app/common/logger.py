import sys

from loguru import logger


def setup_logger() -> None:
    logger.remove()

    logger.add(sys.stdout, format='{time} | {level} | {message}')

    logger.add(
        'logs/app.log',
        format='{time} | {level} | {message}',
        rotation='500 MB',
        retention='15 days',
    )
