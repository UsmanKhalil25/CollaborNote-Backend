import datetime
import json
from app.manager import study_room_manager
from app.manager.study_room_manager import StudyRoomManager
from app.models import study_room
from app.models.study_room import StudyRoom
from app.schemas.participant import Permission
from app.utils import convert_to_pydantic_object_id,convert_to_str
from fastapi import APIRouter,Depends, WebSocket, WebSocketDisconnect

from app.auth.token_manager import TokenManager

from app.controllers.study_room_controller import StudyRoomController

from app.schemas.study_room import StudyRoomCreate, StudyRoomUpdate
from app.schemas.token import TokenData


router = APIRouter(
    prefix="/study-rooms",
     tags=["Study Room"]
)

def get_study_room_controller() -> StudyRoomController:
    return StudyRoomController()

def get_token_manager() -> TokenManager:
    return TokenManager()

study_room_manager=StudyRoomManager()

def get_study_room_manager()->StudyRoomManager:
    return study_room_manager

@router.post("")
async def create_study_room(
    study_room_info: StudyRoomCreate,
    token: TokenData = Depends(get_token_manager().get_current_user),
    study_room_controller: StudyRoomController = Depends(get_study_room_controller),
):
    current_user_id = token.id
    return await study_room_controller.create_study_room(
        current_user_id, study_room_info
    )


@router.get("")
async def list_study_rooms(
    token: TokenData = Depends(get_token_manager().get_current_user),
    study_room_controller:StudyRoomController=Depends(get_study_room_controller)
):
    current_user_id = token.id
    return await study_room_controller.list_study_rooms(
        current_user_id
    )


@router.get("/{study_room_id}")
async def retrieve_study_room(
    study_room_id: str,
    token: TokenData = Depends(get_token_manager().get_current_user),
    study_room_controller: StudyRoomController = Depends(get_study_room_controller)
):
    current_user_id = token.id
    return await study_room_controller.retrieve_study_room(
        current_user_id, study_room_id
    )


@router.put("/{study_room_id}")
async def update_study_room(
    study_room_id: str,
    study_room_data: StudyRoomUpdate,
    token: TokenData = Depends(get_token_manager().get_current_user),
    study_room_controller: StudyRoomController = Depends(get_study_room_controller)
):
    current_user_id = token.id
    return await study_room_controller.update_study_room(
        current_user_id, study_room_id, study_room_data
    )


@router.patch("/{study_room_id}/end")
async def end_study_room(
    study_room_id: str,
    token: TokenData = Depends(get_token_manager().get_current_user),
    study_room_controller: StudyRoomController = Depends(get_study_room_controller),
):
    current_user_id = token.id
    return await study_room_controller.end_study_room(current_user_id, study_room_id)


@router.post("/{study_room_id}/participants")
async def add_participant(
    study_room_id: str,
    token: TokenData = Depends(get_token_manager().get_current_user),
    study_room_controller: StudyRoomController = Depends(get_study_room_controller),
):
    current_user_id = token.id
    return await study_room_controller.add_participant(current_user_id, study_room_id)
    
    
@router.delete("/{study_room_id}/participants/{participant_id}")
async def remove_participant(
    study_room_id: str,
    participant_id: str,
    token: TokenData = Depends(get_token_manager().get_current_user),
    study_room_controller: StudyRoomController = Depends(get_study_room_controller),
):
    current_user_id = token.id
    return await study_room_controller.remove_participant(current_user_id, study_room_id, participant_id)


@router.patch("/{study_room_id}/participants/{participant_id}")
async def update_participant_permission(
    study_room_id: str,
    participant_id: str,
    permission: str,
    token: TokenData = Depends(get_token_manager().get_current_user),
    study_room_controller: StudyRoomController = Depends(get_study_room_controller),
):
    current_user_id = token.id
    return await study_room_controller.update_participant_permission(current_user_id, study_room_id, participant_id, permission)
    

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    study_room_manager: StudyRoomManager = Depends(get_study_room_manager)):
    
    current_user_id = websocket.query_params.get('user_id')
    if not current_user_id:
        await websocket.close(code=4001)  
        return
    await study_room_manager.connect(websocket,current_user_id)
    
    try:
        while True:
            #now listening for study-room document and study-room invitations
            message = await websocket.receive_text() 

            data=json.loads(message)
            study_room_id=data["data"]["study_room_id"]
            study_room = await StudyRoom.get(convert_to_pydantic_object_id(study_room_id))
            
            participant_exists = False
            for participant in study_room.participants:
                if participant.user_id==convert_to_pydantic_object_id(current_user_id):
                    participant_exists=True
                    break
            
            if not participant_exists:
                await websocket.close(code=4001)  # Close WebSocket connection with a custom error code
                return

            if data["type"] == "invitation":
                print("heheheh")
                '''
                {
                    "type":"invitation",
                    "data": {
                        "invited_user_id"="23123131313",
                        "study_room_id"="312312414142"
                    }
                }
                '''
                invited_user_id = data["data"]["invited_user_id"] 
                print(f"invited users ${invited_user_id}")  
                await study_room_manager.send_message(invited_user_id, {
                    "type": "invitation",
                    "data":{
                        "study_room_id": study_room_id,
                        "inviter_id": current_user_id
                    }
                })
            elif data["type"] == "document_update":
                '''
                {   
                    "type":"document_update",
                    "data":{
                        "study_room_id":"312312414142"
                        "content":"33314342"
                    }
                }
                '''
                for participant in study_room.participants:
                    if participant.is_active and participant.user_id != convert_to_pydantic_object_id(current_user_id):
                        message = {
                            "type": "document_update", 
                            "data":{
                                "editor_id": current_user_id , 
                                "study_room_id": study_room_id, 
                                "content": data["data"]["content"]
                            }
                        }
                        await study_room_manager.send_message(
                            convert_to_str(participant.user_id), 
                            message=message  
                        )

    except Exception as e:
        print(e)
        await study_room_manager.disconnect(current_user_id)

