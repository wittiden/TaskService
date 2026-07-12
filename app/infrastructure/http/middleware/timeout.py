import asyncio
from asyncio.exceptions import TimeoutError

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class TimeoutMiddleware(BaseHTTPMiddleware):
    """Middleware по контролю за временем ответа"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:

        try:
            response = await asyncio.wait_for(call_next(request), 15)
        except TimeoutError:
            return JSONResponse(
                status_code=504,
                content={
                    'path': request.url.path,
                    'title': 'Gateway timeout error',
                    'details': 'Waif for timeout error in middleware',
                },
            )

        return response
