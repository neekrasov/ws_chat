from fastapi import APIRouter, WebSocket, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, Response

from api.dependencies.chat import get_chat_service_stub, ChatService
from api.dependencies.auth import get_current_user_stub
from core.settings import get_settings
from db.models import User
import rncryptor


router = APIRouter()
settings = get_settings()
templates = Jinja2Templates(directory="client/templates")


@router.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


@router.get("/connect/{room_id}")
async def accept(
    room_id: str,
    chat_service: ChatService = Depends(get_chat_service_stub),
    user: User = Depends(get_current_user_stub),
):
    chat_info = chat_service.make_chat_info(user, room_id)
    encrypted_chat_info = rncryptor.encrypt(chat_info, settings.encryption_secret)
    return Response(
        headers={"x-data-token": encrypted_chat_info.hex()}, status_code=200
    )


@router.websocket("/ws")
async def ws(data_token: str, websocket: WebSocket):
    username, _ = rncryptor.decrypt(
        bytes.fromhex(data_token), settings.encryption_secret
    ).split(":")

    if username is None:
        await websocket.close()
        return

    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"{username}: {data}")
