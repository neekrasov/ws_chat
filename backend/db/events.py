from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from redis.asyncio import Redis

from db.models.users import User
from core.settings import Settings
from api.dependencies.db import get_mongo, get_redis


def setup_deps(app: FastAPI, settings: Settings):
    mongodb = AsyncIOMotorClient(
        host=settings.mongodb_host,
        port=settings.mongodb_port,
    )
    redis = Redis.from_url(
        f"redis://{settings.redis_host}:{settings.redis_port}", decode_responses=True
    )

    app.dependency_overrides[get_mongo] = lambda: mongodb
    app.dependency_overrides[get_redis] = lambda: redis

    return (mongodb, redis)


async def init_models(settings: Settings, mongodb: AsyncIOMotorClient):
    await init_beanie(
        database=getattr(mongodb, settings.mongodb_name),
        document_models=[User],
    )


async def close_connections(
    mongodb: AsyncIOMotorClient,
    redis: Redis,
):
    await redis.close()
    mongodb.close()
