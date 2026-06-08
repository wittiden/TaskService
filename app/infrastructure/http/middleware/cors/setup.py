from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.http.middleware.cors.config import CORSConfig


def setup_cors(cors_config: CORSConfig, app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_config.ALLOW_ORIGINS.split(','),
        allow_methods=cors_config.ALLOW_METHODS.split(','),
        allow_headers=cors_config.ALLOW_HEADERS.split(','),
    )
