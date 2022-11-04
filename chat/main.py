import logging
import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles

from core.settings import get_settings
from core.logger import LOGGING
from db.events import init_models, setup_deps, close_connections
from api.router import router as api_router
from api.dependencies.auth import get_current_user, fastapi_users_app
from services.context import ChatMiddleware


def create_app(settings) -> FastAPI:
    app = FastAPI(
        title=settings.project_name,
        description=settings.descriprion,
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        default_response_class=ORJSONResponse,
    )

    mongodb, redis = setup_deps(app, settings)
    app.dependency_overrides[get_current_user] = lambda: fastapi_users_app.current_user()

    async def startup():
        await init_models(settings, mongodb)

    async def shutdown():
        await close_connections(mongodb, redis)

    app.add_event_handler("shutdown", shutdown)
    app.add_event_handler("startup", startup)
    app.include_router(
        router=api_router,
        prefix="/api",
    )
    
    app.mount("/client", StaticFiles(directory="client"), name="static")
    app.add_middleware(ChatMiddleware)
    return app


settings = get_settings()
app = create_app(settings)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
        reload=True,
    )
