from functools import cache
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    RedisStrategy,
)
from fastapi import Depends
from redis.asyncio import Redis

from services.manager import UserManager
from db.models.users import get_user_db
from .db import get_redis


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


def get_redis_strategy(redis: Redis = Depends(get_redis)) -> RedisStrategy:
    return RedisStrategy(redis, lifetime_seconds=3600)


@cache
def get_auth_backend():
    auth_backends = AuthenticationBackend(
        name="redis",
        get_strategy=get_redis_strategy,
        transport=BearerTransport(tokenUrl="auth/jwt/login"),
    )
    return auth_backends
