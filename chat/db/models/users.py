from fastapi_users.db import BeanieBaseUser, BeanieUserDatabase
from beanie import PydanticObjectId


class User(BeanieBaseUser[PydanticObjectId]):
    username: str


async def get_user_db() -> BeanieUserDatabase:
    yield BeanieUserDatabase(User)
