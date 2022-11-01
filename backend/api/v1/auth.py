from fastapi_users import FastAPIUsers
from fastapi import APIRouter, Depends
from beanie import PydanticObjectId

from api.dependencies.auth import get_user_manager, get_auth_backend
from schemas.users import UserRead, UserCreate
from db.models.users import User

router = APIRouter()

fastapi_users = FastAPIUsers[User, PydanticObjectId](
    get_user_manager=get_user_manager, auth_backends=[get_auth_backend()]
)

router.include_router(fastapi_users.get_auth_router(get_auth_backend()))

router.include_router(fastapi_users.get_register_router(UserRead, UserCreate))

router.include_router(fastapi_users.get_verify_router(UserRead))

router.include_router(fastapi_users.get_reset_password_router())


@router.get("/me")
async def get_me(user: User = Depends(fastapi_users.current_user())):
    return user
