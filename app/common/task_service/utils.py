from celery import Celery

from app.common.config import application_config
from app.common.task_service.config import task_service_config
from app.infrastructure.redis.config import redis_config


def make_celery() -> Celery | None:
    if application_config.is_test:
        return None

    celery_obj = Celery(
        'TaskServiceCelery',
        broker=f'amqp://{task_service_config.RABBITMQ_USER}:{task_service_config.RABBITMQ_PASSWORD}@{task_service_config.RABBITMQ_HOST}:{task_service_config.RABBITMQ_PORT}//',
        backend=redis_config.redis_db_url,
        include=['app.common.task_service.tasks.send'],
    )

    celery_obj.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        task_track_started=True,
    )

    return celery_obj


celery = make_celery()
