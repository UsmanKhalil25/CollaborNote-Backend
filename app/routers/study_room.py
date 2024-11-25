from fastapi import APIRouter,Depends

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
async def delete_participant(
    study_room_id: str,
    participant_id: str,
    token: TokenData = Depends(get_token_manager().get_current_user),
    study_room_controller: StudyRoomController = Depends(get_study_room_controller),
):
    current_user_id = token.id
    return await study_room_controller.delete_participant(current_user_id, study_room_id, participant_id)


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
    