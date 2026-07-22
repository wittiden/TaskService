from collections.abc import AsyncGenerator, Generator

import pytest
from alembic.command import upgrade
from alembic.config import Config
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from loguru import logger
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import AsyncRedisContainer

from app.bootstrap.application import setup_application
from app.container.container import create_async_container
from app.infrastructure.database.config import database_config
from app.infrastructure.redis.config import redis_config

logger.disable('app.infrastructure.http.lifespan')
logger.disable('app.infrastructure.http.middleware.logger')


@pytest.fixture(scope='session')
def postgres_container() -> Generator[PostgresContainer, None]:
    with PostgresContainer('postgres:16-alpine') as postgres:
        database_config.DB_USER = postgres.username
        database_config.DB_PASS = postgres.password
        database_config.DB_HOST = postgres.get_container_host_ip()
        database_config.DB_PORT = postgres.get_exposed_port(5432)
        database_config.DB_NAME = postgres.dbname

        alembic_config = Config(
            'alembic.ini',
        )
        upgrade(alembic_config, 'head')

        yield postgres


@pytest.fixture(scope='session')
def redis_container():
    with AsyncRedisContainer('redis:8.0-alpine') as redis:
        redis_config.REDIS_PASS = redis.password
        redis_config.REDIS_HOST = redis.get_container_host_ip()
        redis_config.REDIS_PORT = redis.get_exposed_port(6379)
        redis_config.REDIS_DB = 0

        yield redis


@pytest.fixture
async def client(postgres_container, redis_container) -> AsyncGenerator[AsyncClient, None]:
    container = create_async_container()
    app = setup_application(container=container)
    app.state.limiter.enabled = False

    async with (
        LifespanManager(app=app),
        AsyncClient(
            transport=ASGITransport(app=app),
            base_url='http://test',
            timeout=10,
        ) as client,
    ):
        yield client
