import sys
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from loguru import logger
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    if '--uvicorn' in sys.argv:
        logger.info('Application: start on uvicorn server')
    elif '--gunicorn' in sys.argv:
        logger.info('Application: start on gunicorn server')

    yield

    logger.info('Application: end')
