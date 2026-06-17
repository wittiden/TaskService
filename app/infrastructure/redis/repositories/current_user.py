from uuid import UUID

from redis.asyncio import Redis

from app.modules.users.contracts.dtos import UserInfoDTO


class RedisCurrentUserRepository:
    """Репозиторий для работы с текущим пользователем в Redis"""

    def __init__(self, redis_client: Redis) -> None:
        self._redis_client = redis_client

    async def get_current_user(self, user_id: UUID) -> UserInfoDTO | None:
        name = f'user:{str(user_id)}'

        obj = await self._redis_client.get(name)
        if obj is None:
            return None

        return UserInfoDTO.model_validate_json(obj)

    async def set_current_user(self, current_user: UserInfoDTO, ttl: int = 600) -> None:
        name = f'user:{str(current_user.user_id)}'

        await self._redis_client.set(name, current_user.model_dump_json(), ex=ttl)

    async def delete_current_user_from_redis(self, user_id: UUID) -> None:
        name = f'user:{str(user_id)}'

        await self._redis_client.delete(name)
