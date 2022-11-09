import logging
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from core.settings import get_settings
from core.logger import LOGGING
from db.events import init_models, setup_deps, close_connections
from api.router import router as api_router
from api.dependencies.auth import setup_auth_deps
from api.dependencies.chat import setup_service_deps


def create_app(settings) -> FastAPI:
    app = FastAPI(
        title=settings.project_name,
        description=settings.descriprion,
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        default_response_class=ORJSONResponse,
    )

    mongodb, redis = setup_deps(app, settings)
    setup_auth_deps(app)
    setup_service_deps(app)

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
    return app


settings = get_settings()
templates = Jinja2Templates(directory="client/templates")
app = create_app(settings)


@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
        reload=True,
    )
