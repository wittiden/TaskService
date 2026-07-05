from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from app.bootstrap.routers import setup_routers
from app.container.container import async_container
from app.infrastructure.https.lifespan import lifespan


def setup_application() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    setup_dishka(async_container, app)
    setup_routers(app)

    return app
