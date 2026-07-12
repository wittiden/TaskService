import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    if '--uvicorn' in sys.argv:
        logger.info('Application: start on uvicorn server')
    elif '--gunicorn' in sys.argv:
        logger.info('Application: start on gunicorn server')

    yield

    logger.info('Application: end')
