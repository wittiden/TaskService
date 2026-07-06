from uuid import UUID

from redis.asyncio import Redis

from app.modules.users.contracts.dtos import FullUserInfoDTO


class CurrentUserRedisCommandsRepository:
    """Репозиторий Redis с командами для работы с текущим пользователем"""

    def __init__(self, redis_client: Redis) -> None:
        self._redis_client = redis_client

    async def set_current_user(self, current_user: FullUserInfoDTO, ttl: int = 300) -> None:
        name = f'user:{current_user.user_id}'
        key = current_user.model_dump_json()

        await self._redis_client.set(name, key, ex=ttl)

    async def get_current_user(self, user_id: UUID) -> FullUserInfoDTO | None:
        name = f'user:{user_id}'

        obj = await self._redis_client.get(name)

        if obj is None:
            return None

        return FullUserInfoDTO.model_validate_json(obj)

    async def delete_current_user(self, user_id: UUID) -> int:
        name = f'user:{user_id}'

        return await self._redis_client.delete(name)
