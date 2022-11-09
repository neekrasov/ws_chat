from fastapi import Depends, FastAPI
from services.chat import ChatService, RedisService
from .db import (
    get_redis_stub,
    get_room_collection_stub,
    get_message_collection_stub,
    get_user_collection_stub,
)


async def get_redis_service_stub():
    raise NotImplementedError


async def get_chat_service_stub():
    raise NotImplementedError


async def get_redis_service(redis=Depends(get_redis_stub)) -> RedisService:
    return RedisService(redis)


async def get_chat_service(
    redis_service=Depends(get_redis_service_stub),
    room_collection=Depends(get_room_collection_stub),
    message_collection=Depends(get_message_collection_stub),
    user_collection=Depends(get_user_collection_stub),
) -> ChatService:
    return ChatService(
        redis_service, user_collection, room_collection, message_collection
    )


def setup_service_deps(app: FastAPI):
    app.dependency_overrides[get_redis_service_stub] = get_redis_service
    app.dependency_overrides[get_chat_service_stub] = get_chat_service
