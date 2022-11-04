from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    RedisStrategy,
    AuthenticationBackend,
    BearerTransport,
)
from fastapi_users.db import BeanieUserDatabase
from fastapi import Depends
from beanie import PydanticObjectId
from redis.asyncio import Redis

from services.manager import UserManager
from db.models.users import get_user_db, User
from .db import get_redis

def get_current_user():
    raise NotImplementedError

async def get_user_manager(user_db: BeanieUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


def get_redis_strategy(redis: Redis = Depends(get_redis)) -> RedisStrategy:
    return RedisStrategy(redis, lifetime_seconds=3600)


def get_redis_auth_backends() -> AuthenticationBackend:
    return AuthenticationBackend(
        name="jwt",
        get_strategy=get_redis_strategy,
        transport=BearerTransport(tokenUrl="v1/auth/jwt/login"),
    )


def get_fastapi_users_app(auth_backends: list) -> FastAPIUsers:
    return FastAPIUsers[User, PydanticObjectId](
        get_user_manager=get_user_manager, auth_backends=auth_backends
    )

redis_auth_backend = get_redis_auth_backends()
fastapi_users_app = get_fastapi_users_app([redis_auth_backend])
current_user = fastapi_users_app.current_user()