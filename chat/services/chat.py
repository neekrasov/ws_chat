import asyncio
from fastapi.websockets import WebSocket, WebSocketDisconnect
from redis.asyncio import Redis
from db.models import Room, Message, User
from pydantic.error_wrappers import ValidationError
import logging


class RedisService:
    def __init__(self, redis: Redis):
        self._redis = redis

    def _make_user_key(self, username: str) -> str:
        return f"user:{username}"

    def _make_room_key(self, chat_id: str) -> str:
        return f"room:{chat_id}"

    async def add_user_to_room(self, username: str, room_id: str):
        user_key = self._make_user_key(username)
        room_key = self._make_room_key(room_id)
        await self._redis.sadd(room_key, user_key)

    async def remove_user_from_room(self, username: str, room_id: str):
        user_key = self._make_user_key(username)
        room_key = self._make_room_key(room_id)
        await self._redis.srem(room_key, user_key)

    async def get_room_info(self, room_id: str) -> list[User]:
        room_key = self._make_room_key(room_id)
        users = await self._redis.smembers(room_key)
        return [User.parse_raw(user) for user in users]

    async def user_room_exists(self, username: str, room_id: str) -> bool:
        user_key = self._make_user_key(username)
        room_key = self._make_room_key(room_id)
        return await self._redis.sismember(room_key, user_key)

    async def send_message_to_stream(self, room_id: str, fields):
        await self._redis.xadd(
            name=f"room:{room_id}:stream", fields=fields, maxlen=1000
        )

    async def read_data_stream(self, room_id: str, last_id: str = b"$"):
        stream = f"room:{room_id}:stream"
        events = await self._redis.xread(streams={stream: last_id}, block=0)
        return events
    
    async def announce_user(self, room_id: str, username: str):
        await self.send_message_to_stream(room_id, {"type": "announce", "username": username})


class ChatService:
    def __init__(
        self,
        redis_service: RedisService,
        user_collection: User,
        room_collection: Room,
        message_collection: Message,
    ):
        self.redis_service = redis_service
        self._users = user_collection
        self._rooms = room_collection
        self._messages = message_collection

    def make_chat_info(self, user: User, room: Room) -> str:
        return f"{user.id}:{user.username};{room.id}:{room.name}"

    async def create_chat(self, user: User, chat_name: str) -> Room:
        room = await self._rooms.insert_one(
            Room(admin_id=user.id, name=chat_name, members=[user.id])
        )
        return room
    
    async def save_message(self, author: str, text: str, room_id: str) -> Message:
        message = await self._messages.insert_one(Message(author=author, text=text))
        room = await self._rooms.get(room_id)
        room.messages.append(message.id)
        await room.save()
        return message

    async def get_chat(self, room_id: str) -> Room:
        try:
            chat = await self._rooms.get(room_id)
        except ValidationError:
            return None
        return chat

    async def get_user(self, user_id: str) -> User:
        user = await self._users.get(user_id)
        return user

    async def add_user_to_chat(self, user_id, room_id: str) -> Room:
        room = await self._rooms.get(room_id)
        room.members.append(user_id)
        await room.save()
        return room

    async def get_user_chats(self, user_id: str) -> list[Room]:
        rooms = await self._rooms.find(Room.members == user_id).to_list()
        return rooms
    
    async def get_chat_history(self, room_id: str, offset: int = 0, limit: int = 10):
        room = await self._rooms.get(room_id)
        messages = await self._messages\
                        .find_many({"_id": {"$in":room.messages}})\
                        .skip(offset).limit(limit).to_list()
        return messages

    async def ws_receive(self, websocket: WebSocket, username, room_id, user_id):
        await self.redis_service.add_user_to_room(username, room_id)
        await self.redis_service.announce_user(room_id, username)
        try:
            while True:
                message = await websocket.receive_json()

                fields = {
                    "type": "message",
                    "username": username,
                    "message": message,
                    "room": room_id,
                }
                await self.redis_service.send_message_to_stream(room_id, fields)
                await self.save_message(author=user_id, text=message, room_id=room_id)
        except WebSocketDisconnect:
            await self.redis_service.remove_user_from_room(username, room_id)
            await websocket.close()

    async def ws_send(self, websocket: WebSocket, room_id):
        last_id = b"$"
        while True:
            events = await self.redis_service.read_data_stream(room_id, last_id)
            for event in events:
                last_id = event[1][0][0]
                fields = event[1][0][1]
            await websocket.send_json(fields)
            await asyncio.sleep(1)
