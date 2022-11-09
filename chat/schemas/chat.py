from pydantic import BaseModel
from beanie import PydanticObjectId

class ChatCreate(BaseModel):
    name: str

class UserInChatCreate(BaseModel):
    room_id: PydanticObjectId
    user_id: PydanticObjectId
    