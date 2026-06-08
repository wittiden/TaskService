from fastapi import APIRouter, Request

health_router = APIRouter(prefix='/api/v1/health', tags=['health'])


@health_router.get('/app')
def app_health_check_endpoint(request: Request) -> dict[str, str]:
    return {
        'Program': 'healthy'
    }
