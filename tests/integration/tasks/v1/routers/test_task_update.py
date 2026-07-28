from uuid import UUID

import pytest
from fastapi import status

from app.infrastructure.database.model import TaskModel
from app.modules.tasks.contracts.dtos import FullTaskInfoDTO
from tests.factories.task import TasksFactory


class TestUpdateTaskRouters:
    """Тестирование роутеров по обновлению данных задач"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_update_my_task_endpoint_good(self, current_standard):
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

        new_title = 'new_title'
        new_description = 'new_description'
        request_data = {
            'title': new_title,
            'description': new_description,
            'schedule_type': None,
            'important_level': None,
        }

        update_response = await client.patch(
            url=f'/api/v1/tasks/{response_data["task_id"]}', json=request_data
        )
        update_response_data: dict = update_response.json()

        assert update_response.status_code == status.HTTP_200_OK
        assert update_response_data.keys() == FullTaskInfoDTO.model_fields.keys()
        assert update_response_data['title'] == request_data['title']
        assert update_response_data['title'] != task.title
        assert update_response_data['description'] == request_data['description']
        assert update_response_data['description'] != task.description

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_close_my_task_endpoint_good(self, current_standard, async_session):
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

        response = await client.patch(url=f'/api/v1/tasks/close/{task.task_id}')
        response_data: dict = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert response_data.keys() == FullTaskInfoDTO.model_fields.keys()
        assert response_data['closed_at'] is not None
        assert not task.closed_at

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_complete_my_task_endpoint_good(self, current_standard, async_session):
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

        response = await client.patch(url=f'/api/v1/tasks/complete/{task.task_id}')
        response_data: dict = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert response_data.keys() == FullTaskInfoDTO.model_fields.keys()
        assert response_data['completed_at'] is not None
        assert not task.completed_at
