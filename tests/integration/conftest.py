from collections.abc import AsyncGenerator, Generator

import pytest
from alembic.command import upgrade
from alembic.config import Config
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import AsyncRedisContainer

from app.bootstrap.application import setup_application
from app.infrastructure.database.config import database_config
from app.infrastructure.redis.config import redis_config


@pytest.fixture(scope='session')
def postgres_container() -> Generator[PostgresContainer, None]:
    with PostgresContainer('postgres:16-alpine') as postgres:
        database_config.DB_USER = postgres.username
        database_config.DB_PASS = postgres.password
        database_config.DB_HOST = postgres.get_container_host_ip()
        database_config.DB_PORT = postgres.get_exposed_port(5432)
        database_config.DB_NAME = postgres.dbname

        alembic_config = Config('alembic.ini')
        upgrade(alembic_config, 'head')

        yield postgres


@pytest.fixture(scope='session')
async def database_engine(postgres_container) -> AsyncGenerator[AsyncEngine, None]:
    async_engine = create_async_engine(
        url=database_config.database_url,
        echo=False,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        pool_timeout=5,
        connect_args={'command_timeout': 5},
    )

    print(f'Database URL: {database_config.database_url}')

    try:
        yield async_engine
    finally:
        await async_engine.dispose()


@pytest.fixture(scope='session')
def session_factory(database_engine) -> async_sessionmaker:
    return async_sessionmaker(
        bind=database_engine,
        expire_on_commit=False,
        autoflush=False,
    )


@pytest.fixture
async def async_session(session_factory) -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as async_session:
        yield async_session

        await async_session.rollback()


@pytest.fixture(scope='session')
def redis_container() -> Generator[AsyncRedisContainer, None]:
    with AsyncRedisContainer('redis:8.0-alpine') as redis:
        redis_config.REDIS_PASS = redis.password
        redis_config.REDIS_HOST = redis.get_container_host_ip()
        redis_config.REDIS_PORT = redis.get_exposed_port(6379)

        yield redis


@pytest.fixture(scope='session')
async def redis_client(redis_container):
    async with Redis(
        password=redis_config.REDIS_PASS,
        host=redis_config.REDIS_HOST,
        port=redis_config.REDIS_PORT,
        db=redis_config.REDIS_DB,
        decode_responses=True,
        socket_timeout=3,
        socket_connect_timeout=1,
    ) as redis_client:
        try:
            yield redis_client
        finally:
            await redis_client.aclose()


@pytest.fixture
async def client(postgres_container, redis_container) -> AsyncGenerator[AsyncClient, None]:
    app = setup_application()
    app.state.limiter.enabled = False

    async with (
        LifespanManager(app),
        AsyncClient(
            transport=ASGITransport(app=app),
            base_url='http://test',
            timeout=10,
        ) as client,
    ):
        yield client
