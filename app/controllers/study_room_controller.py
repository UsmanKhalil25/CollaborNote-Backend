from app.constants import RESPONSE_STATUS_SUCCESS

from app.schemas.study_room import StudyRoomCreate, StudyRoomUpdate
from app.services.study_room_service import StudyRoomServices

from app.utils import create_response


class StudyRoomController:
    def __init__(self) -> None:
        self.study_room_service = StudyRoomServices()


    async def create_study_room(self, current_user_id: str, study_room_info: StudyRoomCreate):
        study_room = await self.study_room_service.create_study_room(current_user_id, study_room_info)
        return create_response(RESPONSE_STATUS_SUCCESS, "Study Room created successfully", data={"study_room": study_room})
    

    async def list_study_rooms(self, study_room_id: str):
        study_rooms = await self.study_room_service.list_study_rooms(study_room_id)
        return create_response(RESPONSE_STATUS_SUCCESS, "Study rooms listing fetched successfully", data={"study_rooms": study_rooms})


    async def retrieve_study_room(self,current_user_id: str, study_room_id: str):
        study_room = await self.study_room_service.retrieve_study_room(current_user_id, study_room_id)
        return create_response(RESPONSE_STATUS_SUCCESS, "Study rooms information fetched successfully", data={"study_room": study_room})


    async def update_study_room(self,current_user_id:str,study_room_id: str, study_room_data: StudyRoomUpdate):
        await self.study_room_service.update_study_room(current_user_id, study_room_id, study_room_data)
        return create_response(RESPONSE_STATUS_SUCCESS, "Study room updated successfully")


    async def end_study_room(self,current_user_id:str,study_room_id:str):
        await self.study_room_service.end_study_room(current_user_id,study_room_id)
        return create_response(RESPONSE_STATUS_SUCCESS, "Study Room ended successfully")
