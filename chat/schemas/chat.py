from pydantic import BaseModel

class ChatCreate(BaseModel):
    name: str