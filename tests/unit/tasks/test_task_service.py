import copy

import pytest
from pytest_mock import MockerFixture
from sqlalchemy.exc import IntegrityError

from app.modules.tasks.contracts.dtos import FullTaskInfoDTO, SecurityTaskInfoDTO
from app.modules.tasks.exceptions import (
    ClosedTaskError,
    CompletedTaskError,
    TaskInvalidDataError,
    TaskLimitError,
    TaskNotFoundError,
)
from app.modules.users.contracts.dtos import FullUserInfoDTO
from tests.factories.task import TasksFactory
from tests.factories.user import UsersFactory


class TestCreateTaskCase:
    """Тестирование кейса по созданию задач"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_task_good(
        self,
        mock_task_queries_repo,
        mock_task_config,
        mock_task_commands_repo,
        create_task_mock_case,
    ):
        user = UsersFactory.build()
        task = TasksFactory.build()

        mock_task_queries_repo.select_user_tasks_count.return_value = 1
        mock_task_config.STANDARD_TASK_COUNT_LIMIT = 1
        mock_task_config.VIP_TASK_COUNT_LIMIT = 2

        mock_task_commands_repo.insert_task.return_value = task

        result = await create_task_mock_case.create_task(
            FullUserInfoDTO.model_validate(user),
            task.important_level,
            task.schedule_type,
            task.title,
            task.description,
        )

        assert isinstance(result, SecurityTaskInfoDTO)
        assert result.task_id == task.task_id
        assert result.title == task.title
        assert result.description == task.description
        assert result.schedule_type == task.schedule_type
        assert result.important_level == task.important_level
        assert result.completed_at == task.completed_at
        mock_task_queries_repo.select_user_tasks_count.assert_awaited_once_with(user.user_id)
        mock_task_commands_repo.insert_task.assert_awaited_once_with(
            user.user_id, task.important_level, task.schedule_type, task.title, task.description
        )

    @pytest.mark.parametrize(
        'is_vip, count',
        [(False, 2), (True, 3)],
        ids=[
            'standard_count_limit',
            'vip_count_limit',
        ],
    )
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_task_config_bad(
        self,
        mock_task_commands_repo,
        mock_task_config,
        mock_task_queries_repo,
        create_task_mock_case,
        count,
        is_vip,
    ):
        user = UsersFactory.build(vip=is_vip)
        task = TasksFactory.build()

        mock_task_queries_repo.select_user_tasks_count.return_value = count
        mock_task_config.STANDARD_TASK_COUNT_LIMIT = 1
        mock_task_config.VIP_TASK_COUNT_LIMIT = 2

        with pytest.raises(TaskLimitError):
            await create_task_mock_case.create_task(
                FullUserInfoDTO.model_validate(user),
                task.important_level,
                task.schedule_type,
                task.title,
                task.description,
            )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_task_bad(
        self,
        mock_task_commands_repo,
        mock_task_config,
        mock_task_queries_repo,
        create_task_mock_case,
    ):
        user = UsersFactory.build()
        task = TasksFactory.build()

        mock_task_queries_repo.select_user_tasks_count.return_value = 1
        mock_task_config.STANDARD_TASK_COUNT_LIMIT = 1
        mock_task_config.VIP_TASK_COUNT_LIMIT = 2

        mock_task_commands_repo.insert_task.side_effect = IntegrityError(
            statement=None, params=None, orig=Exception('duplicate key')
        )

        with pytest.raises(TaskInvalidDataError):
            await create_task_mock_case.create_task(
                FullUserInfoDTO.model_validate(user),
                task.important_level,
                task.schedule_type,
                task.title,
                task.description,
            )


class TestUpdateTaskCase:
    """Тестирование кейса по обновлению данных задач"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_my_task_params_good(
        self,
        mock_task_queries_repo,
        mock_task_commands_repo,
        mock_create_tack_audit_case,
        update_task_mock_case,
    ):
        task = TasksFactory.build()

        new_title = 'new_title'
        new_description = 'new_description'
        new_params = {
            'title': new_title,
            'description': new_description,
        }

        new_task = copy.copy(task)
        new_task.title = new_title
        new_task.description = new_description

        mock_task_queries_repo.select_user_task_close_complete_params.return_value = {
            'task_id': task.task_id,
            'completed_at': task.completed_at,
            'closed_at': task.closed_at,
            'title': task.title,
            'description': task.description,
            'schedule_type': task.schedule_type,
            'important_level': task.important_level,
        }

        mock_task_commands_repo.alter_user_task_params.return_value = new_task

        result = await update_task_mock_case.update_my_task_params(
            task.user_id, task.task_id, new_params
        )

        assert isinstance(result, FullTaskInfoDTO)
        assert result.title == new_task.title
        assert result.title != task.title
        assert result.description == new_task.description
        assert result.description != task.description
        mock_task_queries_repo.select_user_task_close_complete_params.assert_awaited_once_with(
            task.user_id, task.task_id
        )
        mock_task_commands_repo.alter_user_task_params.assert_awaited_once_with(
            task.user_id, task.task_id, new_params
        )
        assert mock_create_tack_audit_case.create_task_audit.await_count == 2

    @pytest.mark.parametrize(
        'is_close, is_complete, exc_type',
        [
            (True, False, ClosedTaskError),
            (False, True, CompletedTaskError),
        ],
        ids=[
            'closed',
            'completed',
        ],
    )
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_my_task_params_bad(
        self, mock_task_queries_repo, update_task_mock_case, is_close, is_complete, exc_type
    ):
        task = TasksFactory.build(close=is_close, complete=is_complete)

        new_title = 'new_title'
        new_description = 'new_description'
        new_params = {
            'title': new_title,
            'description': new_description,
        }

        mock_task_queries_repo.select_user_task_close_complete_params.return_value = {
            'task_id': task.task_id,
            'completed_at': task.completed_at,
            'closed_at': task.closed_at,
            'title': task.title,
            'description': task.description,
            'schedule_type': task.schedule_type,
            'important_level': task.important_level,
        }

        with pytest.raises(exc_type):
            await update_task_mock_case.update_my_task_params(
                task.user_id, task.task_id, new_params
            )


class TestDeleteTaskCase:
    """Тестирование кейса по удалению задач"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_user_task_by_id_good(
        self, mocker: MockerFixture, mock_task_commands_repo, delete_task_mock_case
    ):
        task = TasksFactory.build()

        mock_task_commands_repo.delete_user_task_by_id.return_value = mocker.Mock()

        await delete_task_mock_case.delete_user_task_by_id(task.task_id, task.user_id)

        mock_task_commands_repo.delete_user_task_by_id.assert_awaited_once_with(
            task.task_id, task.user_id
        )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_user_task_by_id_bad(self, mock_task_commands_repo, delete_task_mock_case):
        task = TasksFactory.build()

        mock_task_commands_repo.delete_user_task_by_id.return_value = None

        with pytest.raises(TaskNotFoundError):
            await delete_task_mock_case.delete_user_task_by_id(task.task_id, task.user_id)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_user_tasks_good(
        self, mocker: MockerFixture, mock_task_commands_repo, delete_task_mock_case
    ):
        task = TasksFactory.build()

        mock_task_commands_repo.delete_user_tasks.return_value = mocker.Mock()

        await delete_task_mock_case.delete_user_tasks(task.user_id)

        mock_task_commands_repo.delete_user_tasks.assert_awaited_once_with(task.user_id)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_close_complete_user_tasks_good(
        self, mocker: MockerFixture, mock_task_commands_repo, delete_task_mock_case
    ):
        task = TasksFactory.build()

        mock_task_commands_repo.delete_close_complete_user_tasks.return_value = mocker.Mock()

        await delete_task_mock_case.delete_close_complete_user_tasks(task.user_id)

        mock_task_commands_repo.delete_close_complete_user_tasks.assert_awaited_once_with(
            task.user_id
        )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_close_user_tasks_good(
        self, mocker: MockerFixture, mock_task_commands_repo, delete_task_mock_case
    ):
        task = TasksFactory.build()

        mock_task_commands_repo.delete_close_user_tasks.return_value = mocker.Mock()

        await delete_task_mock_case.delete_close_user_tasks(task.user_id)

        mock_task_commands_repo.delete_close_user_tasks.assert_awaited_once_with(task.user_id)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_complete_user_tasks_good(
        self, mocker: MockerFixture, mock_task_commands_repo, delete_task_mock_case
    ):
        task = TasksFactory.build()

        mock_task_commands_repo.delete_complete_user_tasks.return_value = mocker.Mock()

        await delete_task_mock_case.delete_complete_user_tasks(task.user_id)

        mock_task_commands_repo.delete_complete_user_tasks.assert_awaited_once_with(task.user_id)


class TestManageTaskCase:
    """Тестирование кейса по менедженгу задач"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_close_my_task_good(
        self, mock_task_commands_repo, mock_create_tack_audit_case, manage_task_mock_case
    ):
        task = TasksFactory.build(close=True)

        mock_task_commands_repo.alter_close_user_task.return_value = task

        result = await manage_task_mock_case.close_my_task(task.user_id, task.task_id)

        assert isinstance(result, FullTaskInfoDTO)
        mock_task_commands_repo.alter_close_user_task.assert_awaited_once_with(
            task.user_id, task.task_id
        )
        assert mock_create_tack_audit_case.create_task_audit.await_count == 1

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_complete_my_task_good(
        self, mock_task_commands_repo, mock_create_tack_audit_case, manage_task_mock_case
    ):
        task = TasksFactory.build(complete=True)

        mock_task_commands_repo.alter_complete_user_task.return_value = task

        result = await manage_task_mock_case.complete_my_task(task.user_id, task.task_id)

        assert isinstance(result, FullTaskInfoDTO)
        mock_task_commands_repo.alter_complete_user_task.assert_awaited_once_with(
            task.user_id, task.task_id
        )
        assert mock_create_tack_audit_case.create_task_audit.await_count == 1

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_close_my_task_bad(self, mock_task_commands_repo, manage_task_mock_case):
        task = TasksFactory.build(close=True)

        mock_task_commands_repo.alter_close_user_task.return_value = None

        with pytest.raises(TaskNotFoundError):
            await manage_task_mock_case.close_my_task(task.user_id, task.task_id)
