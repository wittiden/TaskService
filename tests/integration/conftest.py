from collections.abc import AsyncGenerator, Generator

import pytest
from alembic.command import upgrade
from alembic.config import Config
from asgi_lifespan import LifespanManager
from fastapi import status
from httpx import ASGITransport, AsyncClient
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
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
def container(postgres_container, redis_container):
    return create_async_container()


@pytest.fixture
async def async_session(container) -> AsyncGenerator[AsyncSession, None]:
    async with container() as async_container:
        session = await async_container.get(AsyncSession)

        yield session


@pytest.fixture
async def client(
    postgres_container, redis_container, container
) -> AsyncGenerator[AsyncClient, None]:
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


async def _current(client, url, is_admin=False, is_vip=False) -> AsyncClient:
    user = UsersFactory(admin=is_admin, vip=is_vip)
    request_data = {
        'name': user.name,
        'email': user.email,
        'password': user.password_hash,
    }

    response = await client.post(url=url, json=request_data)
    assert response.status_code == status.HTTP_201_CREATED

    login_request_data = {
        'email': user.email,
        'password': user.password_hash,
    }
    login_response = await client.post(
        url='/api/v1/auth/login',
        json=login_request_data,
    )
    login_response_data = login_response.json()
    assert login_response.status_code == status.HTTP_200_OK

    client.headers = {
        'Authorization': f'Bearer {login_response_data["access_token"]}',
        'Content-Type': 'application/json',
    }

    return client


@pytest.fixture
async def current_standard(client) -> AsyncClient:
    return await _current(client, '/api/v1/users/standard')


@pytest.fixture
async def current_admin(client) -> AsyncClient:
    return await _current(client, '/api/v1/users/admin', is_admin=True)


@pytest.fixture
async def current_vip(client) -> AsyncClient:
    return await _current(client, '/api/v1/users/vip', is_vip=True)
