from fastapi import APIRouter
from schemas.users import UserRead, UserCreate
from api.dependencies.auth import fastapi_users_app, redis_auth_backend

router = APIRouter()

router.include_router(
    fastapi_users_app.get_auth_router(redis_auth_backend), prefix="/jwt"
)

router.include_router(fastapi_users_app.get_register_router(UserRead, UserCreate))

router.include_router(fastapi_users_app.get_verify_router(UserRead))

router.include_router(fastapi_users_app.get_reset_password_router())
