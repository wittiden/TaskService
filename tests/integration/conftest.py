from collections.abc import AsyncGenerator, Generator

import pytest
from alembic.command import upgrade
from alembic.config import Config
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from loguru import logger
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
from app.container.container import create_async_container
from app.infrastructure.database.config import database_config
from app.infrastructure.redis.config import redis_config
from tests.factories.user import UsersFactory

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

        alembic_config = Config('alembic.ini')
        upgrade(alembic_config, 'head')

        yield postgres


# ✅ Раскомментировано
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

    try:
        yield async_engine
    finally:
        await async_engine.dispose()


# ✅ Раскомментировано
@pytest.fixture(scope='session')
def async_session_factory(database_engine) -> async_sessionmaker:
    return async_sessionmaker(
        bind=database_engine,
        autoflush=False,
        expire_on_commit=False,
    )


@pytest.fixture
async def async_session(async_session_factory) -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as async_session:
        yield async_session


@pytest.fixture(scope='session')
def redis_container() -> Generator[AsyncRedisContainer, None]:
    with AsyncRedisContainer('redis:8.0-alpine') as redis:
        redis_config.REDIS_PASS = redis.password
        redis_config.REDIS_HOST = redis.get_container_host_ip()
        redis_config.REDIS_PORT = redis.get_exposed_port(6379)
        redis_config.REDIS_DB = 0

        yield redis


@pytest.fixture(scope='session')
async def redis_client(redis_container) -> AsyncGenerator[Redis, None]:
    async with Redis(
        host=redis_config.REDIS_HOST,
        port=redis_config.REDIS_PORT,
        password=redis_config.REDIS_PASS,
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
    container = create_async_container()

    app = setup_application(container=container)
    app.state.limiter.enabled = False

    async with (
        LifespanManager(app=app),
        AsyncClient(
            transport=ASGITransport(app=app),
            base_url='http://tests',
            timeout=10,
        ) as async_client,
    ):
        yield async_client


async def _row_user(client, is_admin: bool = False, is_vip: bool = False):
    user = UsersFactory(admin=is_admin, vip=is_vip)
    password = 'TestPassword123!'  # ✅ Оригинальный пароль

    request_data = {
        'name': user.name,
        'email': user.email,
        'password': password,  # ✅ Оригинальный пароль
    }

    url = '/api/v1/users/standard'
    if is_admin:
        url = '/api/v1/users/admin'
    elif is_vip:  # ✅ elif, чтобы не перезаписать admin
        url = '/api/v1/users/vip'

    await client.post(
        url=url,
        json=request_data,
    )

    login_request_data = {
        'email': request_data['email'],
        'password': password,  # ✅ Оригинальный пароль
    }

    login_response = await client.post(
        '/api/v1/auth/login',
        json=login_request_data,
    )
    login_response_data = login_response.json()

    client.headers = {
        'Authorization': f'Bearer {login_response_data["access_token"]}',
        'Content-Type': 'application/json',
    }

    return client


@pytest.fixture
async def current_standard(client):
    return await _row_user(client)


@pytest.fixture
async def current_admin(client):
    return await _row_user(client, is_admin=True)


@pytest.fixture
async def current_vip(client):
    return await _row_user(client, is_vip=True)


@pytest.fixture
async def user(client):
    user = UsersFactory()
    password = 'TestPassword123!'

    request_data = {
        'name': user.name,
        'email': user.email,
        'password': password,
    }

    response = await client.post('/api/v1/users/standard', json=request_data)

    return response.json()
