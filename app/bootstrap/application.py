from dishka import AsyncContainer
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.bootstrap.handlers import setup_handlers
from app.bootstrap.middlewares import setup_middlewares
from app.bootstrap.routers import setup_routers
from app.common.limiter.config import limiter
from app.container.container import async_container
from app.infrastructure.http.lifespan import lifespan
from app.infrastructure.http.middleware.CORS.config import cors_config
from app.infrastructure.http.middleware.CORS.setup import setup_cors


def setup_application(container: AsyncContainer = async_container) -> FastAPI:
    app = FastAPI(title='TaskService', version='2.0.0', lifespan=lifespan)

    Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=True,
        excluded_handlers=['/health', '/metrics'],
    ).instrument(app).expose(app, include_in_schema=True, should_gzip=True)

    app.state.limiter = limiter

    setup_dishka(container, app)

    setup_middlewares(app)
    setup_cors(app, cors_config)

    setup_handlers(app)

    setup_routers(app)

    return app
