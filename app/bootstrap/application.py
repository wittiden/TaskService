from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from app.bootstrap.handlers import setup_handlers
from app.bootstrap.middlewares import setup_middlewares
from app.bootstrap.routers import setup_routers
from app.container.container import async_container
from app.infrastructure.http.lifespan import lifespan
from app.infrastructure.http.middleware.CORS.config import cors_config
from app.infrastructure.http.middleware.CORS.setup import setup_cors


def setup_application() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    setup_dishka(async_container, app)

    setup_middlewares(app)
    setup_cors(app, cors_config)

    setup_handlers(app)

    setup_routers(app)

    return app
