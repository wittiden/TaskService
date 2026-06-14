import asyncio
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from fastapi import Response, Request

from app.infrastructure.http.middleware.exceptions import HTTPTimeoutError


class TimeoutMiddleware(BaseHTTPMiddleware):
    """Middleware для ограничения времени на ответ"""

    def __init__(self, app: FastAPI, timeout: int) -> None:
        super().__init__(app)

        self._timeout = timeout

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            response = await asyncio.wait_for(call_next(request), self._timeout)

            return response
        except asyncio.TimeoutError:
            raise HTTPTimeoutError('HTTP timeout error in middleware guard')
