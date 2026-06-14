from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from fastapi import Request, Response
from loguru import logger
from time import perf_counter
from uuid import uuid4


class MiddlewareLogger(BaseHTTPMiddleware):
    """Middleware для логирования"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if not request.url.path.startswith('/api/v1'):
            return await call_next(request)

        start_time = perf_counter()
        request_id = str(uuid4())
        request.state.request_id = request_id

        response = await call_next(request)

        time_process = (perf_counter() - start_time) * 1000

        response.headers['X-Request-ID'] = str(request_id)
        response.headers['X-Process-Time'] = f'{time_process:.2f}'
        response.headers['X-API-Version'] = '1.0.0'

        info_str = f'{request_id} | {request.method} {request.url.path} | {response.status_code} | {time_process:.2f} ms'

        try:
            logger.info(info_str)
        except Exception as ex:
            logger.error(info_str)
            raise ex

        return response
