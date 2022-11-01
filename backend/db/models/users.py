from fastapi_users.db import BeanieBaseUser, BeanieUserDatabase
from beanie import PydanticObjectId


class User(BeanieBaseUser[PydanticObjectId]):
    pass


async def get_user_db():
    yield BeanieUserDatabase(User)
