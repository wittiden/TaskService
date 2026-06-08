from fastapi import FastAPI
from dishka.integrations.fastapi import setup_dishka

from app.common.bootstrap.middlewares import setup_middlewares
from app.common.bootstrap.routers import setup_routers
from app.di.container import async_container
from app.infrastructure.http.lifespan import lifespan
from app.infrastructure.http.middleware.cors.config import CORSConfig
from app.infrastructure.http.middleware.cors.setup import setup_cors
from app.infrastructure.http.server.config import ServerConfig
from app.infrastructure.http.server.start_server import start_server_with_setup

def main() -> None:

    app = FastAPI(lifespan=lifespan)
    setup_dishka(container=async_container, app=app)

    cors_config = CORSConfig()
    setup_cors(cors_config, app)

    setup_middlewares(app)
    setup_routers(app)

    server_config = ServerConfig()
    start_server_with_setup(server_config, app)


if __name__ == '__main__':
    main()
