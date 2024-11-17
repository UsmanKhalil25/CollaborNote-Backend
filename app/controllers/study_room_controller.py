from typing import List
from app.constants import RESPONSE_STATUS_SUCCESS
from app.models import user
from app.models.study_room import StudyRoom
from app.schemas import StudyRoomCreate, StudyRoomInfoUpdate
from app.services.study_room_services import StudyRoomServices
from app.utils import create_response


class StudyRoomController:
    def __init__(self) -> None:
        self.study_room_service=StudyRoomServices()


    ## Study Room Operations

    
    async def create_study_room(self,current_user_id:str,study_room_info:StudyRoomCreate):
        await self.study_room_service.create_study_room(current_user_id,study_room_info)
        return create_response(RESPONSE_STATUS_SUCCESS, "Study Room created successfully")
    
    async def end_study_room(self,current_user_id:str,study_room_id:str):
        await self.study_room_service.end_study_room(current_user_id,study_room_id)
        return create_response(RESPONSE_STATUS_SUCCESS, "Study Room ended successfully")
    
    async def transfer_study_room_ownership(self,current_user_id:str,new_owner_id:str,study_room_id:str):
        await self.study_room_service.transfer_study_room_ownership(current_user_id,new_owner_id,study_room_id)
        return create_response(RESPONSE_STATUS_SUCCESS, "Ownership transfered successfully")
    
    async def update_study_room_info(self,current_user_id:str,study_room_id:str,study_room_info:StudyRoomInfoUpdate):
        await self.study_room_service.update_study_room_info(current_user_id,study_room_id,study_room_info)
        return create_response(RESPONSE_STATUS_SUCCESS, "Study Room info updated successfully")
    
    async def update_study_room_markdown_content(self,current_user_id:str,study_room_id:str,markdown_data:str):
        await self.study_room_service.update_study_room_markdown_content(current_user_id,study_room_id,markdown_data)
        return create_response(RESPONSE_STATUS_SUCCESS, "MarkDown Content updated successfully")
    
    async def get_study_rooms_owned_by_user(self,current_user_id:str):
        return await self.study_room_service.get_study_rooms_owned_by_user(current_user_id)

    async def get_study_room(self,study_room_id:str):
        return await self.study_room_service.get_study_room(study_room_id)
    
    async def get_study_room_participants(self,current_user_id:str,study_room_id:str):
        return await self.study_room_service.get_study_room_participants(current_user_id,study_room_id)
    

    ## Participant Operations


    async def get_study_rooms_participated_by_user(self,current_user_id:str):
        return await self.study_room_service.get_study_rooms_participated_by_user(current_user_id)
    
    async def join_study_room(self,current_user_id:str,study_room_id:str):
        await self.study_room_service.join_study_room(current_user_id,study_room_id)
        return create_response(RESPONSE_STATUS_SUCCESS, "User added successfully")
    
    async def remove_user_from_study_room(self,user_id:str,current_user_id:str,study_room_id:str):
        await self.study_room_service.remove_user_from_study_room(user_id,current_user_id,study_room_id)
        return create_response(RESPONSE_STATUS_SUCCESS, "User removed successfully")
    
    async def leave_study_room(self,current_user_id:str,study_room_id:str):
        await self.study_room_service.leave_study_room(current_user_id,study_room_id)
        return create_response(RESPONSE_STATUS_SUCCESS, "You are removed from study room successfully")
   
   
    ## Permission Management


    async def grant_edit_permission(self,user_id:str,current_user_id:str,study_room_id:str):
        await self.study_room_service.grant_edit_permission(user_id,current_user_id,study_room_id)
        return create_response(RESPONSE_STATUS_SUCCESS, "Edit permission granted successfully")
    
    async def revoke_edit_permission(self,user_id:str,current_user_id:str,study_room_id:str):
        await self.study_room_service.revoke_edit_permission(user_id,current_user_id,study_room_id)
        return create_response(RESPONSE_STATUS_SUCCESS, "Edit permission revoked successfully.")
    