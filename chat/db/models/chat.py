from beanie import Document, PydanticObjectId
from .users import User


class Message(Document):
    author: User
    text: str

    class Settings:
        name = "messages"


class Room(Document):
    name: str
    members: list[PydanticObjectId]
    messages: list[PydanticObjectId] = []

    class Settings:
        name = "rooms"


async def get_room_db() -> Room:
    yield Room


async def get_message_db() -> Message:
    yield Message
