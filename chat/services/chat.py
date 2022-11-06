from redis.asyncio import Redis
from db.models import Room, Message, User


class RedisService:
    def __init__(self, redis: Redis):
        self._redis = redis

    def _make_user_key(self, user_id: str, username: str) -> str:
        return f"user:{user_id}:{username}"

    def _make_room_key(self, chat_id: str) -> str:
        return f"room:{chat_id}"

    async def add_user_to_room(self, user_id: str, username: str, room_id: str):
        user_key = self._make_user_key(user_id, username)
        room_key = self._make_room_key(room_id)
        await self._redis.sadd(room_key, user_key)

    async def remove_user_from_room(self, user_id: str, username: str, room_id: str):
        user_key = self._make_user_key(user_id, username)
        room_key = self._make_room_key(room_id)
        await self._redis.srem(room_key, user_key)

    async def get_room_info(self, room_id: str) -> list[User]:
        room_key = self._make_room_key(room_id)
        users = await self._redis.smembers(room_key)
        return [User.parse_raw(user) for user in users]

    async def user_room_exists(self, user_id: str, username: str, room_id: str) -> bool:
        user_key = self._make_user_key(user_id, username)
        room_key = self._make_room_key(room_id)
        return await self._redis.sismember(room_key, user_key)


class ChatService:
    def __init__(
        self,
        redis_service: RedisService,
        room_collection: Room,
        message_collection: Message,
    ):
        self.redis_service = redis_service
        self._rooms = room_collection
        self._messages = message_collection

    def make_chat_info(self, user: User, room_id: str) -> dict:
        return f"{user.username}:{room_id}"

    async def create_chat(self, user: User, chat_name: str) -> Room:
        room = await self._rooms.insert_one(Room(name=chat_name))
        await self.redis_service.add_user_to_room(user.id, user.username, room.id)
        return room
