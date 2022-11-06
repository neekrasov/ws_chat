from fastapi_users import schemas
from beanie import PydanticObjectId


class UserRead(schemas.BaseUser[PydanticObjectId]):
    username: str


class UserCreate(schemas.BaseUserCreate):
    username: str

class UserUpdate(schemas.BaseUserUpdate):
    username: str
