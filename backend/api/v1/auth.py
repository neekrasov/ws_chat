from fastapi_users import FastAPIUsers
from fastapi import APIRouter
from beanie import PydanticObjectId
from fastapi_users.authentication import AuthenticationBackend, BearerTransport

from api.dependencies.auth import get_user_manager, get_redis_strategy
from schemas.users import UserRead, UserCreate
from db.models.users import User

router = APIRouter()

bearer_transport = BearerTransport(tokenUrl="v1/auth/jwt/login")

auth_backends = AuthenticationBackend(
    name="jwt",
    get_strategy=get_redis_strategy,
    transport=bearer_transport,
)

fastapi_users_app = FastAPIUsers[User, PydanticObjectId](
    get_user_manager=get_user_manager, auth_backends=[auth_backends]
)

router.include_router(fastapi_users_app.get_auth_router(auth_backends), prefix="/jwt")

router.include_router(fastapi_users_app.get_register_router(UserRead, UserCreate))

router.include_router(fastapi_users_app.get_verify_router(UserRead))

router.include_router(fastapi_users_app.get_reset_password_router())
