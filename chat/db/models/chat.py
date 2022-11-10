from beanie import Document, PydanticObjectId


class Message(Document):
    author: PydanticObjectId
    text: str

    class Settings:
        name = "messages"


class Room(Document):
    admin_id: PydanticObjectId
    name: str
    members: list[PydanticObjectId]
    messages: list[PydanticObjectId] = []

    class Settings:
        name = "rooms"


async def get_room_db() -> Room:
    yield Room


async def get_message_db() -> Message:
    yield Message
