from starlette.requests import Request
from slowapi.util import get_remote_address


def get_remote_user(request: Request):
    if hasattr(request.state, 'user_id'):
        return f'user:{request.state.user_id}'

    else:
        return f'ip:{get_remote_address(request)}'
