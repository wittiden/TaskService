from fastapi import Request
from fastapi.responses import JSONResponse, Response
from slowapi.errors import RateLimitExceeded

from app.common.exceptions.base_exception import RouterError


def app_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    path = f'{request.method} {request.url.path}'

    if isinstance(exc, RouterError):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                'path': path,
                'title': exc.title,
                'details': exc.details,
            }
        )

    return JSONResponse(
        status_code=500,
        content={
            'path': path,
            'title': 'Internal Server Error',
            'details': 'An unexpected error occurred',
        }
    )


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Build a simple JSON response that includes the details of the rate limit
    that was hit. If no limit is hit, the countdown is added to headers.
    """
    response = JSONResponse(
        {
            "path": request.url.path,
            "title": "Rate limit exceeded",
            "details": f"Too many requests: {exc.detail}"
        },
        status_code=429
    )
    response = request.app.state.limiter._inject_headers(
        response, request.state.view_rate_limit
    )
    return response
