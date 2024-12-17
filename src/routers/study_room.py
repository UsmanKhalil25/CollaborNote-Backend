import datetime
import json
from src.manager import study_room_manager
from src.manager.study_room_manager import StudyRoomManager
from src.documents import study_room
from src.documents.study_room import StudyRoom
from src.schemas.participant import Permission
from src.utils import convert_to_pydantic_object_id, convert_to_str
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from src.services.token_manager import TokenManager

from src.controllers.study_room_controller import StudyRoomController

from src.schemas.study_room import StudyRoomCreate, StudyRoomUpdate
from src.schemas.token import TokenData


router = APIRouter(prefix="/study-rooms", tags=["Study Room"])


def get_study_room_controller() -> StudyRoomController:
    return StudyRoomController()


def get_token_manager() -> TokenManager:
    return TokenManager()


study_room_manager = StudyRoomManager()


def get_study_room_manager() -> StudyRoomManager:
    return study_room_manager


@router.post("")
async def create_study_room(
    study_room_info: StudyRoomCreate,
    token: TokenData = Depends(get_token_manager().verify_token),
    study_room_controller: StudyRoomController = Depends(get_study_room_controller),
):
    current_user_id = token.id
    return await study_room_controller.create_study_room(
        current_user_id, study_room_info
    )


@router.get("")
async def list_study_rooms(
    token: TokenData = Depends(get_token_manager().verify_token),
    study_room_controller: StudyRoomController = Depends(get_study_room_controller),
):
    current_user_id = token.id
    return await study_room_controller.list_study_rooms(current_user_id)


@router.get("/{study_room_id}")
async def retrieve_study_room(
    study_room_id: str,
    token: TokenData = Depends(get_token_manager().verify_token),
    study_room_controller: StudyRoomController = Depends(get_study_room_controller),
):
    current_user_id = token.id
    return await study_room_controller.retrieve_study_room(
        current_user_id, study_room_id
    )


@router.put("/{study_room_id}")
async def update_study_room(
    study_room_id: str,
    study_room_data: StudyRoomUpdate,
    token: TokenData = Depends(get_token_manager().verify_token),
    study_room_controller: StudyRoomController = Depends(get_study_room_controller),
):
    current_user_id = token.id
    return await study_room_controller.update_study_room(
        current_user_id, study_room_id, study_room_data
    )


@router.patch("/{study_room_id}/end")
async def end_study_room(
    study_room_id: str,
    token: TokenData = Depends(get_token_manager().verify_token),
    study_room_controller: StudyRoomController = Depends(get_study_room_controller),
):
    current_user_id = token.id
    return await study_room_controller.end_study_room(current_user_id, study_room_id)


@router.post("/{study_room_id}/participants")
async def add_participant(
    study_room_id: str,
    token: TokenData = Depends(get_token_manager().verify_token),
    study_room_controller: StudyRoomController = Depends(get_study_room_controller),
):
    current_user_id = token.id
    return await study_room_controller.add_participant(current_user_id, study_room_id)


@router.delete("/{study_room_id}/participants/{participant_id}")
async def remove_participant(
    study_room_id: str,
    participant_id: str,
    token: TokenData = Depends(get_token_manager().verify_token),
    study_room_controller: StudyRoomController = Depends(get_study_room_controller),
):
    current_user_id = token.id
    return await study_room_controller.remove_participant(
        current_user_id, study_room_id, participant_id
    )


@router.patch("/{study_room_id}/participants/{participant_id}")
async def update_participant_permission(
    study_room_id: str,
    participant_id: str,
    permission: str,
    token: TokenData = Depends(get_token_manager().verify_token),
    study_room_controller: StudyRoomController = Depends(get_study_room_controller),
):
    current_user_id = token.id
    return await study_room_controller.update_participant_permission(
        current_user_id, study_room_id, participant_id, permission
    )


@router.get("/{study_room_id}/invitations/search")
async def search_invitation_by_room(
    study_room_id: str,
    query: str,
    token: TokenData = Depends(get_token_manager().verify_token),
    study_room_controller: StudyRoomController = Depends(get_study_room_controller),
):
    current_user_id = token.id
    return await study_room_controller.search_invitation_by_room(
        current_user_id, study_room_id, query
    )


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    study_room_manager: StudyRoomManager = Depends(get_study_room_manager),
):
    current_user_id = websocket.query_params.get("user_id")
    if not current_user_id:
        await websocket.close(code=4001)
        return

    await study_room_manager.connect(websocket, current_user_id)

    async def handle_document_update(data):
        study_room_id = data["data"]["study_room_id"]
        study_room = await StudyRoom.get(convert_to_pydantic_object_id(study_room_id))
        message = {
            "type": "document_update",
            "data": {
                "editor_id": current_user_id,
                "study_room_id": study_room_id,
                "content": data["data"]["content"],
            },
        }
        await notify_participants(study_room, current_user_id, message)

    async def handle_room_end(data):
        study_room_id = data["data"]["study_room_id"]
        study_room = await StudyRoom.get(convert_to_pydantic_object_id(study_room_id))
        message = {
            "type": "room_end",
            "data": {
                "study_room_id": study_room_id,
                "message": "The study session has ended.",
            },
        }
        await notify_participants(study_room, current_user_id, message)

    async def notify_participants(study_room, editor_id, message):
        for participant in study_room.participants:
            if (
                participant.is_active
                and participant.user_id != convert_to_pydantic_object_id(editor_id)
            ):
                await study_room_manager.send_message(
                    convert_to_str(participant.user_id), message=message
                )

    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            if data["type"] == "document_update":
                await handle_document_update(data)
            elif data["type"] == "room_end":
                await handle_room_end(data)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if current_user_id in study_room_manager.connections:
            await study_room_manager.disconnect(current_user_id)
        else:
            print(f"Warning: user {current_user_id} was not found in the connections.")
