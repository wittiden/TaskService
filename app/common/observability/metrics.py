from fastapi import FastAPI
from fastapi.routing import APIRoute
from prometheus_fastapi_instrumentator import Instrumentator, metrics

from app.common.config import application_config


def setup_prometheus(app: FastAPI) -> None:
    if application_config.is_test:
        return

    prometheus_instrument = Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=True,
        excluded_handlers=['/health', '/metrics', '/openapi.json', '/docs'],
    )

    prometheus_instrument.instrument(app).expose(
        app, should_gzip=True, endpoint='/metrics', include_in_schema=True
    )

    prometheus_instrument.add(
        metrics.latency(),
        metrics.request_size(),
        metrics.response_size(),
        metrics.combined_size(),
    )

    for route in app.routes:
        if (
            isinstance(route, APIRoute)
            and route.path == '/metrics'
            and route.methods is not None
            and 'GET' in route.methods
        ):
            route.tags = ['observability']
