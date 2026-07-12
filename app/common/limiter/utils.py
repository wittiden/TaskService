from slowapi.util import get_remote_address
from starlette.requests import Request


def get_remote_user(request: Request):
    if hasattr(request.state, 'user_id'):
        return f'user:{request.state.user_id}'

    else:
        return f'ip:{get_remote_address(request)}'
