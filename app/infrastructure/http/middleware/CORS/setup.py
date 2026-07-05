from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.http.middleware.CORS.config import CORSConfig


def setup_cors(app: FastAPI, cors_config: CORSConfig) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_config.allow_origins,
        allow_methods=cors_config.allow_methods,
        allow_headers=cors_config.allow_headers,
        allow_credentials=cors_config.ALLOW_CREDENTIALS,
    )
