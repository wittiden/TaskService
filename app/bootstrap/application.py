from fastapi import FastAPI
from dishka.integrations.fastapi import setup_dishka

from app.bootstrap.handlers import setup_handlers
from app.bootstrap.middlewares import setup_middlewares
from app.bootstrap.routers import setup_routers
from app.container.container import async_container
from app.infrastructure.http.lifespan import lifespan
from app.infrastructure.http.middleware.cors.config import cors_config
from app.infrastructure.http.middleware.cors.setup import setup_cors


def setup_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    setup_dishka(async_container, app)
    setup_handlers(app)
    setup_cors(cors_config, app)
    setup_middlewares(app)
    setup_routers(app)

    return app
