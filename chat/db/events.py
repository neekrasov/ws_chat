from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from redis.asyncio import Redis

from db.models import User, Room, Message
from db.models.chat import get_message_db, get_room_db
from db.models.users import get_user_db
from core.settings import Settings
from api.dependencies.db import (
    get_mongo_stub,
    get_redis_stub,
    get_message_collection_stub,
    get_room_collection_stub,
    get_user_collection_stub,
)


def setup_deps(app: FastAPI, settings: Settings):
    mongodb = AsyncIOMotorClient(
        host=settings.mongodb_host,
        port=settings.mongodb_port,
    )
    redis = Redis.from_url(
        f"redis://{settings.redis_host}:{settings.redis_port}", decode_responses=True
    )

    app.dependency_overrides[get_mongo_stub] = lambda: mongodb
    app.dependency_overrides[get_redis_stub] = lambda: redis
    app.dependency_overrides[get_message_collection_stub] = get_message_db
    app.dependency_overrides[get_room_collection_stub] = get_room_db
    app.dependency_overrides[get_user_collection_stub] = get_user_db

    return (mongodb, redis)


async def init_models(settings: Settings, mongodb: AsyncIOMotorClient):
    await init_beanie(
        database=getattr(mongodb, settings.mongodb_name),
        document_models=[User, Room, Message],
    )


async def close_connections(
    mongodb: AsyncIOMotorClient,
    redis: Redis,
):
    await redis.close()
    mongodb.close()
