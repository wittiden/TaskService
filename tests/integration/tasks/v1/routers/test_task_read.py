from uuid import UUID

import pytest
from fastapi import status

from app.infrastructure.database.model import TaskModel
from app.modules.tasks.contracts.dtos import FullTaskInfoDTO
from tests.factories.task import TasksFactory


class TestReadTaskRouters:
    """Тестирование роутеров чтения задач"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_show_user_tasks_endpoint_good(self, current_standard):
        client, _ = current_standard

        response = await client.get(url='/api/v1/tasks/')

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_show_user_active_tasks_endpoint_good(self, current_standard):
        client, _ = current_standard

        response = await client.get(url='/api/v1/tasks/active')

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_show_user_completed_tasks_endpoint_good(self, current_standard):
        client, _ = current_standard

        response = await client.get(url='/api/v1/tasks/completed')

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_show_user_closed_tasks_endpoint_good(self, current_standard):
        client, _ = current_standard

        response = await client.get(url='/api/v1/tasks/closed')

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_show_user_task_by_id_endpoint_good(self, current_standard, async_session):
        client, user_id = current_standard

        task = TasksFactory()
        task_model = TaskModel(
            task_id=task.task_id,
            user_id=UUID(user_id),
            created_at=task.created_at,
            closed_at=task.closed_at,
            completed_at=task.completed_at,
            title=task.title,
            description=task.description,
            important_level=task.important_level,
            schedule_type=task.schedule_type,
        )
        async_session.add(task_model)
        await async_session.commit()

        response = await client.get(url=f'/api/v1/tasks/{task.task_id}')

        assert response.status_code == status.HTTP_200_OK
        assert response.json().keys() == FullTaskInfoDTO.model_fields.keys()
