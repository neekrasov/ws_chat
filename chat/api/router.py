from fastapi import APIRouter

from api.v1.auth import router as auth_router
from api.v1.auth import fastapi_users_app
from api.v1.chat import router as chat_router

from schemas.users import UserRead, UserUpdate

router = APIRouter(
    prefix="/v1",
)

router.include_router(
    router=auth_router,
    prefix="/auth",
    tags=["auth"],
)

router.include_router(
    fastapi_users_app.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

router.include_router(
    router=chat_router,
    prefix="/chat",
    tags=["chat"], 
)
