import pytest
from fastapi import status

from app.modules.tasks.contracts.dtos import SecurityTaskInfoDTO
from tests.factories.task import TasksFactory


class TestCreateTaskRouters:
    """Тестирование роутеров по созданию задач"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_task_endpoint_good(self, current_standard):
        client, _ = current_standard

        task = TasksFactory()
        request_data = {
            'important_level': task.important_level,
            'schedule_type': task.schedule_type,
            'title': task.title,
            'description': task.description,
        }

        response = await client.post(url='/api/v1/tasks/', json=request_data)
        response_data: dict = response.json()

        assert response.status_code == status.HTTP_201_CREATED
        assert response_data.keys() == SecurityTaskInfoDTO.model_fields.keys()
        assert response_data['title'] == task.title
        assert response_data['description'] == task.description
        assert response_data['important_level'] == task.important_level
        assert response_data['schedule_type'] == task.schedule_type
