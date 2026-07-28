from uuid import UUID

import pytest
from fastapi import status

from app.infrastructure.database.model import TaskModel
from tests.factories.task import TasksFactory


class TestDeleteTaskRouters:
    """Тестирование роутеров удалению задач"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_delete_user_task_by_id_endpoint_good(self, current_standard, async_session):
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

        response = await client.delete(url=f'/api/v1/tasks/{task.task_id}')

        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_delete_user_tasks_endpoint_good(self, current_standard, async_session):
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

        response = await client.delete(url='/api/v1/tasks/')

        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.parametrize(
        'is_close, is_complete, url',
        [
            (True, False, '/api/v1/tasks/closed-completed'),
            (False, True, '/api/v1/tasks/closed-completed'),
            (True, False, '/api/v1/tasks/closed'),
            (False, True, '/api/v1/tasks/completed'),
        ],
        ids=[
            'close_in_closed_completed',
            'complete_in_closed_completed',
            'close_in_closed',
            'complete_in_completed',
        ],
    )
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_delete_close_complete_user_tasks_endpoint_good(
        self, current_standard, async_session, is_complete, is_close, url
    ):
        client, user_id = current_standard

        task = TasksFactory(close=is_close, complete=is_complete)
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

        response = await client.delete(url=url)

        assert response.status_code == status.HTTP_204_NO_CONTENT, response.json()
