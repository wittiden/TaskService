from fastapi import Request
from fastapi.responses import JSONResponse

from app.common.exceptions.base_ex import RouterError


def app_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    path = f'{request.method} {request.url.path}',

    if isinstance(exc, RouterError):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                'path': path,
                'title': exc.title,
                'detail': exc.detail,
            }
        )

    return JSONResponse(
        status_code=500,
        content={
            'path': path,
            'title': 'Internal Server Error',
            'detail': 'An unexpected error occurred',        }
    )
