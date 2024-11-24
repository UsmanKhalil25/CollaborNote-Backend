from fastapi import HTTPException, status
from beanie import PydanticObjectId
from typing import List, Optional

from app.models.user import User
from app.models.study_room import StudyRoom

from app.schemas.participant import Permission, ParticipantCreate, ParticipantOut, Participant
from app.schemas.study_room import StudyRoomCreate, StudyRoomListingOut, StudyRoomDetailOut, StudyRoomUpdate

from app.utils import convert_to_pydantic_object_id, validate_object_id


class StudyRoomServices:
    
    @staticmethod
    async def is_user_in_active_room(user_id: PydanticObjectId) -> bool:
        existing_room = await StudyRoom.find_one(
            {"participants.user_id": user_id, "is_active": True}
        )
        return existing_room is not None
    

    @staticmethod
    def is_user_participant(user_id: PydanticObjectId, study_room: StudyRoom) -> bool:
        return any(participant.user_id == user_id for participant in study_room.participants)
    
    
    @staticmethod
    async def map_participant_to_out(participant: Participant) -> ParticipantOut:
        user = await User.get(participant.user_id)

        if user:
            return ParticipantOut(
                user_id=participant.user_id,
                is_owner=participant.is_owner,
                is_active=participant.is_active,
                permission=participant.permission,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
            )
        return None
    

    @staticmethod
    def find_participant_by_user_id(study_room: StudyRoom, user_id: PydanticObjectId) -> Optional[Participant]:
        return next(
            (participant for participant in study_room.participants if str(participant.user_id) ==  str(user_id)), 
            None
        )
    

    def is_user_owner(self, study_room: StudyRoom, user_id: PydanticObjectId) -> bool:
        participant = self.find_participant_by_user_id(study_room, user_id)
        return participant is not None and participant.is_owner


    async def create_study_room(
        self, current_user_id: str, study_room_info: StudyRoomCreate
    ) -> StudyRoom:
        validate_object_id(current_user_id)
        current_user_object_id = convert_to_pydantic_object_id(current_user_id)

        if await self.is_user_in_active_room(current_user_object_id):
            raise HTTPException(
                status_code=400, detail="User is already in an active study room."
            )

        participant = ParticipantCreate(
            user_id=current_user_object_id,
            is_owner=True,
            is_active=True,
            permission=Permission.can_edit,
        )

        participants = [participant.model_dump()]  

        new_study_room = StudyRoom(
            name=study_room_info.name,
            description=study_room_info.description,
            participants=participants,
            is_active=True,
        )

        await new_study_room.insert()
        
        return new_study_room


    async def list_study_rooms(self,current_user_id: str) -> List[StudyRoomListingOut]:
        validate_object_id(current_user_id)
        current_user_object_id = convert_to_pydantic_object_id(current_user_id)

        rooms = await StudyRoom.find(
            {"participants.user_id": current_user_object_id}
        ).to_list()

        study_rooms_with_participants = []

        for room in rooms:
            participants_out = []
            for participant in room.participants:
                participant_out = await self.map_participant_to_out(participant)
                if participant_out:
                    participants_out.append(participant_out)

            study_room = StudyRoomListingOut(
                id=str(room.id),
                name=room.name,
                description=room.description,
                participants=participants_out,
            )
            study_rooms_with_participants.append(study_room)

        return study_rooms_with_participants


    async def retrieve_study_room(self, current_user_id: str, study_room_id: str) -> Optional[StudyRoomDetailOut]:
        validate_object_id(current_user_id)
        current_user_object_id = convert_to_pydantic_object_id(current_user_id)
        
        validate_object_id(study_room_id)
        study_room_object_id = convert_to_pydantic_object_id(study_room_id)
        
        study_room = await StudyRoom.get(study_room_object_id)

        if not study_room:
            raise HTTPException(status_code=404, detail="Study room not found")

        if not self.is_user_participant(current_user_object_id, study_room):
            raise HTTPException(status_code=403, detail="You are not a participant of this study room")

        participants_out = []
        for participant in study_room.participants:
            participant_out = await self.map_participant_to_out(participant)
            if participant_out:
                participants_out.append(participant_out)

        return StudyRoomDetailOut(
            id=str(study_room.id),
            name=study_room.name,
            description=study_room.description,
            participants=participants_out,
            content=study_room.content,
            is_active=study_room.is_active,
            created_at=study_room.created_at,
            ended_at=study_room.ended_at
        )


    async def update_study_room(self, current_user_id:str, study_room_id: str, update_data: StudyRoomUpdate):

        validate_object_id(current_user_id)
        current_user_object_id = convert_to_pydantic_object_id(current_user_id)
        
        validate_object_id(study_room_id)
        study_room_object_id = convert_to_pydantic_object_id(study_room_id)
        
        study_room = await StudyRoom.get(study_room_object_id)

        if not study_room:
            raise HTTPException(status_code=404, detail="Study room not found")

        if not self.is_user_participant(current_user_object_id, study_room):
            raise HTTPException(status_code=403, detail="You are not a participant of this study room")

        if not self.is_user_owner(study_room, current_user_object_id):
            raise HTTPException(status_code=403, detail="You don't have permissions to update this study room")

        if update_data.name:
            study_room.name = update_data.name
        if update_data.description:
            study_room.description = update_data.description
        if update_data.content:
            study_room.content = update_data.content
        if update_data.is_active is not None:
            study_room.is_active = update_data.is_active

        await study_room.save()
    

    async def end_study_room(self, current_user_id: str, study_room_id: str):

        validate_object_id(current_user_id)
        current_user_object_id = convert_to_pydantic_object_id(current_user_id)
        
        validate_object_id(study_room_id)
        study_room_object_id = convert_to_pydantic_object_id(study_room_id)
        
        study_room = await StudyRoom.get(study_room_object_id)

        if not study_room:
            raise HTTPException(status_code=404, detail="Study room not found")

        if not self.is_user_participant(current_user_object_id, study_room):
            raise HTTPException(status_code=403, detail="You are not a participant of this study room")
        
        if not self.is_user_owner(study_room, current_user_object_id):
            raise HTTPException(status_code=403, detail="You don't have permissions to update this study room")
        
        for participant in study_room.participants:
            participant.is_active = False

        study_room.is_active = False

        await study_room.save()

