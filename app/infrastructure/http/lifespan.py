import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from loguru import logger
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    if '--uvicorn' in sys.argv:
        logger.info('Start program on uvicorn server')
    if '--gunicorn' in sys.argv:
        logger.info('Start program on gunicorn server')

    yield

    logger.info('End program')
