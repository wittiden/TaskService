from time import perf_counter
from uuid import uuid4

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from starlette.requests import Request


class LoggerMiddleware(BaseHTTPMiddleware):
    """Middleware по логированию ответов"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = uuid4()
        now = perf_counter()

        response = await call_next(request)

        if not '/api/v1' in request.url.path:
            return response

        process_time = (perf_counter() - now) * 1000
        process_time_str = f'{process_time:.2f} ms'
        logger_str = f'{request_id} | {request.url.path} | {response.status_code} | {process_time:.2f} ms'

        if 200 <= response.status_code < 300:
            logger.info(logger_str)
        else:
            logger.error(logger_str)

        response.headers['X-Request-ID'] = str(request_id)
        response.headers['X-Process-Time'] = process_time_str
        response.headers['X-API-Version'] = '1'

        return response
