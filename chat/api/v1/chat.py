import rncryptor
from fastapi import APIRouter, WebSocket, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, Response
from fastapi.exceptions import HTTPException

from api.dependencies.chat import get_chat_service_stub, ChatService
from api.dependencies.auth import get_current_user_stub
from core.settings import get_settings
from db.models import User, Room
from schemas.chat import ChatCreate
import logging
import asyncio



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
    room = await chat_service.get_chat(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    logging.info(f"User `{user.username}` trying to connect to room `{room.name}` ")
    
    if user.id not in room.members:
        raise HTTPException(status_code=403, detail="User is not a member of this room")
    
    chat_info = chat_service.make_chat_info(user, room)
    encrypted_chat_info = rncryptor.encrypt(chat_info, settings.encryption_secret)
    return Response(
        headers={"x-data-token": encrypted_chat_info.hex()}, status_code=200
    )

@router.post("/create", response_model=Room)
async def create_chat(
    chat: ChatCreate,
    chat_service: ChatService = Depends(get_chat_service_stub),
    user: User = Depends(get_current_user_stub),
):
    room = await chat_service.create_chat(user, chat.name)
    return room

@router.websocket("/ws")
async def ws(
    data_token: str, 
    websocket: WebSocket,
    chat_service: ChatService = Depends(get_chat_service_stub),
):
    user_info, room_info = rncryptor.decrypt(
        bytes.fromhex(data_token), settings.encryption_secret
    ).split(";")
    
    user_id, username = user_info.split(":")
    room_id, room_name = room_info.split(":")

    if user_id is None:
        await websocket.close()
        return

    await websocket.accept()
    await asyncio.gather(
        chat_service.ws_receive(websocket, username, room_id),
        chat_service.ws_send(websocket, room_id)
    )


