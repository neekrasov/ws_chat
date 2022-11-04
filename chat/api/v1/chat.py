from fastapi import APIRouter, WebSocket, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter()

templates = Jinja2Templates(directory="client/templates")

@router.get("/", response_class=HTMLResponse)
async def get(
    request: Request
):
    return templates.TemplateResponse("chat.html", {"request": request})

@router.websocket("/ws")
async def ws(
    websocket: WebSocket
):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(data)

