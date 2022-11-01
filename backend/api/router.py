from fastapi import APIRouter

from api.v1.auth import router as auth_router

router = APIRouter(
    prefix="/v1",
)
router.include_router(
    router=auth_router,
    prefix="/auth",
    tags=["auth"],
)
