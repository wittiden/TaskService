import sys
from fastapi import FastAPI

from app.infrastructure.http.server.adapters import UvicornServer, GunicornServer
from app.infrastructure.http.server.config import ServerConfig


def start_server_with_setup(server_config: ServerConfig, application: FastAPI) -> None:
    if '--uvicorn' in sys.argv:
        UvicornServer(server_config).run_server(application)
    elif '--gunicorn' in sys.argv:
        GunicornServer(server_config).run_server(application)
