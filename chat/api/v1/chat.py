import rncryptor
from fastapi import APIRouter, WebSocket, Depends

from fastapi.responses import Response
from fastapi.exceptions import HTTPException

from api.dependencies.chat import get_chat_service_stub, ChatService
from api.dependencies.auth import get_current_user_stub
from core.settings import get_settings
from db.models import User, Room
from schemas.chat import ChatCreate, UserInChatCreate
import asyncio
import json


router = APIRouter()
settings = get_settings()


@router.get("/connect/{room_id}")
async def accept(
    room_id: str,
    chat_service: ChatService = Depends(get_chat_service_stub),
    user: User = Depends(get_current_user_stub),
):
    room = await chat_service.get_chat(room_id)

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if user.id not in room.members:
        raise HTTPException(status_code=403, detail="User is not a member of this room")

    chat_info = chat_service.make_chat_info(user, room)
    encrypted_chat_info = rncryptor.encrypt(chat_info, settings.encryption_secret)
    return Response(
        content=json.dumps(
            room.dict(exclude={"id", "members", "messages", "admin_id"})
        ),
        media_type="application/json",
        headers={"x-data-token": encrypted_chat_info.hex()},
        status_code=200,
    )


@router.post("/create", response_model=Room)
async def create_chat(
    chat: ChatCreate,
    chat_service: ChatService = Depends(get_chat_service_stub),
    user: User = Depends(get_current_user_stub),
):
    room = await chat_service.create_chat(user, chat.name)
    return room


@router.post("/add-user")
async def add_user_to_chat(
    create_data: UserInChatCreate,
    chat_service: ChatService = Depends(get_chat_service_stub),
    initiator: User = Depends(get_current_user_stub),
):
    user_id = create_data.user_id
    room_id = create_data.room_id

    room = await chat_service.get_chat(room_id)
    user = await chat_service.get_user(str(user_id))

    if initiator.id != room.admin_id:
        raise HTTPException(
            status_code=403, detail="You do not have permission to add a user"
        )

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if user_id in room.members:
        raise HTTPException(status_code=403, detail="User is already in this chat")

    await chat_service.add_user_to_chat(user_id, room_id)
    return Response(status_code=200)


@router.get(
    "/get-my", response_model=list[Room], response_model_exclude={"messages", "members"}
)
async def get_my_chats(
    chat_service: ChatService = Depends(get_chat_service_stub),
    user: User = Depends(get_current_user_stub),
):
    rooms = await chat_service.get_user_chats(user.id)
    return rooms


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
        chat_service.ws_send(websocket, room_id),
    )
