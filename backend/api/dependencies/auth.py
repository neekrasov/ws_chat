from fastapi_users.authentication import RedisStrategy

from fastapi_users.db import BeanieUserDatabase
from fastapi import Depends
from redis.asyncio import Redis

from services.manager import UserManager
from db.models.users import get_user_db
from .db import get_redis


async def get_user_manager(user_db: BeanieUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


def get_redis_strategy(redis: Redis = Depends(get_redis)) -> RedisStrategy:
    return RedisStrategy(redis, lifetime_seconds=3600)
