from abc import ABC
from abc import abstractmethod
from typing import Any

import uvicorn
from fastapi import FastAPI

from app.infrastructure.http.server.config import ServerConfig


class ServerAdapter(ABC):
    """Адаптер для конфигурации разных серверов"""

    @abstractmethod
    def configurate_server(self) -> dict[str, Any]:
        """Метод для сборки конфигурации сервера"""

    @abstractmethod
    def run_server(self, application: FastAPI) -> None:
        """Метод для запуска разных серверов"""


class UvicornServer(ServerAdapter):
    """Класс для конфигурации и запуска uvicorn сервера"""

    def __init__(self, server_config: ServerConfig) -> None:
        self._server_config = server_config

    def configurate_server(self) -> dict[str, Any]:
        return {
            'host': self._server_config.SERVER_HOST,
            'port': self._server_config.SERVER_PORT,
            'reload': self._server_config.SERVER_RELOAD,
            'timeout_keep_alive': self._server_config.SERVER_TIMEOUT,
            'access_log': self._server_config.SERVER_UVICORN_ACCESS_LOG,
        }

    def run_server(self, application: FastAPI) -> None:
        uvicorn.run(application, **self.configurate_server())


class GunicornServer(ServerAdapter):
    """Класс для конфигурации и запуска gunicorn сервера"""

    def __init__(self, server_config: ServerConfig) -> None:
        self._server_config = server_config

    def configurate_server(self) -> dict[str, Any]:
        return {
            'bind': f'{self._server_config.SERVER_HOST}:{self._server_config.SERVER_PORT}',
            'workers': self._server_config.SERVER_WORKERS,
            'worker_class': self._server_config.SERVER_WORKER_CLASS,
            'reload': self._server_config.SERVER_RELOAD,
            'timeout': self._server_config.SERVER_TIMEOUT,
            'accesslog': self._server_config.SERVER_GUNICORN_ACCESS_LOG,
        }

    def run_server(self, application: FastAPI) -> None:
        from gunicorn.app.base import BaseApplication

        class GunicornApplication(BaseApplication):

            def __init__(self, app: FastAPI, options: dict) -> None:
                self._app = app
                self._options = options

                super().__init__()

            def load_config(self):
                for key, value in self._options.items():
                    if key in self.cfg.settings and value is not None:
                        self.cfg.set(key.lower(), value)

            def load(self) -> FastAPI:
                return self._app

        GunicornApplication(application, self.configurate_server()).run()
