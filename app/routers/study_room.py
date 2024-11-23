from datetime import datetime
from typing import List
from fastapi import APIRouter,Depends, FastAPI, HTTPException, WebSocket,status
import gridfs
from app.auth.token_manager import TokenManager
from app.controllers import study_room_controller
from app.controllers.study_room_controller import StudyRoomController
from app.managers import study_room_manager
from app.managers.study_room_manager import StudyRoomManager
from app.models.study_room import StudyRoom
from app.schemas import MarkDownData, StudyRoomCreate, StudyRoomInfoUpdate, StudyRoomOut, TokenData
from app.utils import convert_to_pydantic_object_id


router = APIRouter(
    prefix="/study-room",
     tags=["Study Room"]
)


def get_study_room_controller() -> StudyRoomController:
    return StudyRoomController()

def get_token_manager() -> TokenManager:
    return TokenManager()


# 1
study_room_manager = StudyRoomManager()

def get_study_room_manager()->StudyRoomManager:
    return study_room_manager


# # 2
# def get_study_room_manager()->StudyRoomManager:
#     return StudyRoomManager()




## Study Room Operations


@router.post('/')
async def create_study_room(
    study_room_info:StudyRoomCreate,
    token: TokenData = Depends(get_token_manager().get_current_user),
    study_room_controller:StudyRoomController=Depends(get_study_room_controller)
):
    current_user_id=token.id
    return await study_room_controller.create_study_room(current_user_id,study_room_info)


@router.patch("/{study_room_id}")
async def end_study_room(
    study_room_id:str,
    token: TokenData = Depends(get_token_manager().get_current_user),
    study_room_controller:StudyRoomController=Depends(get_study_room_controller)
):
    current_user_id=token.id
    return await study_room_controller.end_study_room(current_user_id,study_room_id)


@router.patch("/{study_room_id}/change-owner/{new_owner_id}")
async def transfer_study_room_ownership(
    study_room_id: str,
    new_owner_id: str,
    token: TokenData = Depends(get_token_manager().get_current_user),
    study_room_controller: StudyRoomController = Depends(get_study_room_controller)
):
    current_user_id = token.id
    return await study_room_controller.transfer_study_room_ownership(current_user_id, new_owner_id, study_room_id)


@router.patch("/{study_room_id}/info")
async def update_study_room_info(
    study_room_id:str,
    study_room_info:StudyRoomInfoUpdate,
    token: TokenData = Depends(get_token_manager().get_current_user),
    study_room_controller:StudyRoomController=Depends(get_study_room_controller)
):
    current_user_id=token.id
    return await study_room_controller.update_study_room_info(current_user_id,study_room_id,study_room_info)


@router.patch("/{study_room_id}/markdown")
async def update_study_room_markdown_content(
    study_room_id:str,
    markdown_content:MarkDownData,
    token: TokenData = Depends(get_token_manager().get_current_user),
    study_room_controller:StudyRoomController=Depends(get_study_room_controller)
):
    current_user_id=token.id
    return await study_room_controller.update_study_room_markdown_content(current_user_id,study_room_id,markdown_content.markdown_data)


@router.get("/{study_room_id}")
async def get_study_room(
    study_room_id: str,
    token: TokenData = Depends(get_token_manager().get_current_user),
    study_room_controller: StudyRoomController = Depends(get_study_room_controller)
):
    study_room = await study_room_controller.get_study_room(study_room_id) 
    return study_room


@router.get("/")
async def get_study_rooms_owned_by_user(
    owned:bool=True,
    token: TokenData = Depends(get_token_manager().get_current_user),
    study_room_controller:StudyRoomController=Depends(get_study_room_controller)
):
    current_user_id=token.id
    if not owned:
        return await study_room_controller.get_study_rooms_participated_by_user(current_user_id)
    return await study_room_controller.get_study_rooms_owned_by_user(current_user_id)


## Participant Operations


@router.get("/{study_room_id}/participants")
async def get_study_room_participants(
    study_room_id: str,
    token: TokenData = Depends(get_token_manager().get_current_user),
    study_room_controller: StudyRoomController = Depends(get_study_room_controller)
):
    current_user_id = token.id
    return await study_room_controller.get_study_room_participants(current_user_id, study_room_id)


@router.post("/{study_room_id}/join")
async def join_study_room(
    study_room_id:str,
    token: TokenData = Depends(get_token_manager().get_current_user),
    study_room_controller:StudyRoomController=Depends(get_study_room_controller)
):
    current_user_id=token.id
    return await study_room_controller.join_study_room(current_user_id,study_room_id)


@router.patch("/{study_room_id}/leave")
async def leave_study_room(
    study_room_id:str,
    token: TokenData = Depends(get_token_manager().get_current_user),
    study_room_controller:StudyRoomController=Depends(get_study_room_controller)
):
    current_user_id=token.id
    return await study_room_controller.leave_study_room(current_user_id,study_room_id)


@router.patch("/{study_room_id}/remove/{user_id}")
async def remove_user_from_study_room(
    study_room_id:str,
    user_id:str,
    token: TokenData = Depends(get_token_manager().get_current_user),
    study_room_controller:StudyRoomController=Depends(get_study_room_controller)
):
    current_user_id=token.id
    return await study_room_controller.remove_user_from_study_room(user_id,current_user_id,study_room_id)


###  Permission Management


@router.patch("/{study_room_id}/participants/{user_id}/edit-permission/")
async def grant_edit_permission(
    study_room_id:str,
    user_id:str,
    grant:bool=True,
    token: TokenData = Depends(get_token_manager().get_current_user),
    study_room_controller:StudyRoomController=Depends(get_study_room_controller)
):
    current_user_id=token.id
    
    if not grant:
        return await study_room_controller.revoke_edit_permission(user_id,current_user_id,study_room_id)
    return await study_room_controller.grant_edit_permission(user_id,current_user_id,study_room_id)



@router.delete("/study-rooms")
async def delete_all_study_rooms():
    result = await StudyRoom.delete_all() 
    if result.deleted_count > 0:
        return {"message": f"{result.deleted_count} study rooms deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="No study rooms found to delete")



# call after user has give edit permission and close if permission is revoked.
@router.websocket("/ws/{study_room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    study_room_id: str, 
    study_room_manager: StudyRoomManager = Depends(get_study_room_manager)):
   
    current_user_id = websocket.query_params.get('user_id')
    if not current_user_id:
        await websocket.close(code=4001)  
        return
    current_user_object_id=convert_to_pydantic_object_id(current_user_id)
    
    try:
        study_room = await StudyRoom.get(convert_to_pydantic_object_id(study_room_id))

        # Step 1: Authenticate and authorize
        participant = None
        for p in study_room.active_participants:
            if p["participant_id"] == current_user_object_id:
                participant = p
                break

        if not participant:
            await websocket.close(code=4001) 
            return

    
        # Step 2: Accept connection only if authorized
        await study_room_manager.connect(websocket, study_room_id=study_room_id, user_id=current_user_id)

        while True:
            data = await websocket.receive_text()

            if(participant.get("can_edit")):
                
                await study_room_manager.send_message_to_room(
                    study_room_id=study_room_id,
                    user_id=current_user_id,
                    message=data
                )
            
            study_room.markdown_content = data
            study_room.last_modified = datetime.now()
            await study_room.save()

    except Exception as e:
        print(f"Error: {str(e)}")
        await study_room_manager.disconnect(study_room_id=study_room_id, user_id=current_user_id)


@router.websocket("/ws")
async def webSOcketFunction():
    pass