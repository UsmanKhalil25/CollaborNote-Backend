from fastapi import HTTPException
from beanie import PydanticObjectId
from typing import List, Optional

from app.models.user import User
from app.models.study_room import StudyRoom

from app.schemas.participant import Permission, ParticipantCreate, ParticipantOut, Participant
from app.schemas.study_room import StudyRoomCreate, StudyRoomListingOut, StudyRoomDetailOut, StudyRoomUpdate

from app.utils import convert_to_pydantic_object_id, validate_object_id


class StudyRoomService:

    async def get_study_room_or_404(self, study_room_id: PydanticObjectId) -> StudyRoom:

        study_room = await StudyRoom.get(study_room_id)
        if not study_room:
            raise HTTPException(status_code=404, detail="Study room not found")
        return study_room


    def ensure_study_room_is_active(self, study_room: StudyRoom):
        if not study_room.is_active:
            raise HTTPException(
                status_code=403, detail="The study room is not active"
            )


    def ensure_user_is_participant(self, user_id: PydanticObjectId, study_room: StudyRoom):
        if not self.is_user_participant(user_id, study_room):
            raise HTTPException(
                status_code=403, detail="You are not a participant of this study room"
            )


    def ensure_user_is_owner(self, user_id: PydanticObjectId, study_room: StudyRoom):
        if not self.is_user_owner(study_room, user_id):
            raise HTTPException(
                status_code=403, detail="You don't have permissions to perform this action"
            )


    def find_participant(self, study_room: StudyRoom, user_id: PydanticObjectId) -> Participant:
        participant = self.find_participant_by_user_id(user_id, study_room)
        if not participant:
            raise HTTPException(
                status_code=403, detail="The given user is not a participant of this study room"
            )
        return participant


    @staticmethod
    async def is_user_in_active_room(user_id: PydanticObjectId) -> bool:
        existing_room = await StudyRoom.find_one(
            {"participants.user_id": user_id, "is_active": True}
        )
        return existing_room is not None


    @staticmethod
    def is_user_participant(user_id: PydanticObjectId, study_room: StudyRoom) -> bool:
        return any(participant.user_id == user_id and participant.is_active for participant in study_room.participants)


    def is_user_owner(self, study_room: StudyRoom, user_id: PydanticObjectId) -> bool:
        participant = self.find_participant_by_user_id(user_id, study_room)
        return participant is not None and participant.is_owner


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
    def find_participant_by_user_id(user_id: PydanticObjectId, study_room: StudyRoom) -> Optional[Participant]:
        return next(
            (participant for participant in study_room.participants if participant.user_id == user_id), None
        )


    async def create_study_room(self, current_user_id: str, study_room_info: StudyRoomCreate) -> StudyRoom:
        validate_object_id(current_user_id)

        current_user_object_id = convert_to_pydantic_object_id(current_user_id)

        if await self.is_user_in_active_room(current_user_object_id):
            raise HTTPException(status_code=400, detail="User is already in an active study room.")

        participants = [
            ParticipantCreate(
                user_id=current_user_object_id,
                is_owner=True,
                is_active=True,
                permission=Permission.can_edit,
            ).model_dump()
        ]

        new_study_room = StudyRoom(
            name=study_room_info.name,
            description=study_room_info.description,
            participants=participants,
            is_active=True,
        )

        await new_study_room.insert()
        participants_out = [
                await self.map_participant_to_out(participant) for participant in new_study_room.participants if participant
            ]

        return StudyRoomDetailOut(
            id=str(new_study_room.id),
            name=new_study_room.name,
            description=new_study_room.description,
            participants=participants_out,
            content=new_study_room.content,
            is_active=new_study_room.is_active,
            created_at=new_study_room.created_at,
            ended_at=new_study_room.ended_at,
        )


    async def list_study_rooms(self, current_user_id: str) -> List[StudyRoomListingOut]:
        validate_object_id(current_user_id)

        current_user_object_id = convert_to_pydantic_object_id(current_user_id)
        rooms = await StudyRoom.find({"participants.user_id": current_user_object_id}).to_list()

        study_rooms_with_participants = []
        for room in rooms:
            participants_out = [
                await self.map_participant_to_out(participant) for participant in room.participants if participant
            ]

            study_rooms_with_participants.append(
                StudyRoomListingOut(
                    id=str(room.id),
                    name=room.name,
                    description=room.description,
                    created_at=room.created_at,
                    participants=participants_out,
                )
            )
        return study_rooms_with_participants


    async def retrieve_study_room(self, current_user_id: str, study_room_id: str) -> Optional[StudyRoomDetailOut]:
        validate_object_id(current_user_id)
        validate_object_id(study_room_id)

        current_user_object_id = convert_to_pydantic_object_id(current_user_id)
        study_room_object_id = convert_to_pydantic_object_id(study_room_id)

        study_room = await self.get_study_room_or_404(study_room_object_id)
        self.ensure_user_is_participant(current_user_object_id, study_room)

        participants_out = [
            await self.map_participant_to_out(participant) for participant in study_room.participants if participant
        ]

        return StudyRoomDetailOut(
            id=str(study_room.id),
            name=study_room.name,
            description=study_room.description,
            participants=participants_out,
            content=study_room.content,
            is_active=study_room.is_active,
            created_at=study_room.created_at,
            ended_at=study_room.ended_at,
        )


    async def update_study_room(self, current_user_id: str, study_room_id: str, update_data: StudyRoomUpdate):
        validate_object_id(current_user_id)
        validate_object_id(study_room_id)

        current_user_object_id = convert_to_pydantic_object_id(current_user_id)
        study_room_object_id = convert_to_pydantic_object_id(study_room_id)
        
        study_room = await self.get_study_room_or_404(study_room_object_id)

        self.ensure_study_room_is_active(study_room)
        self.ensure_user_is_participant(current_user_object_id, study_room)
        self.ensure_user_is_owner(current_user_object_id, study_room)

        for key, value in update_data.model_dump(exclude_unset=True).items():
            setattr(study_room, key, value)

        await study_room.save()


    async def end_study_room(self, current_user_id: str, study_room_id: str):
        validate_object_id(current_user_id)
        validate_object_id(study_room_id)

        current_user_object_id = convert_to_pydantic_object_id(current_user_id)
        study_room_object_id = convert_to_pydantic_object_id(study_room_id)

        study_room = await self.get_study_room_or_404(study_room_object_id)

        self.ensure_study_room_is_active(study_room)
        self.ensure_user_is_participant(current_user_object_id, study_room)
        self.ensure_user_is_owner(current_user_object_id, study_room)

        for participant in study_room.participants:
            participant.is_active = False
        study_room.is_active = False

        await study_room.save()


    async def add_participant(self, current_user_id: str, study_room_id: str):
        validate_object_id(current_user_id)
        validate_object_id(study_room_id)

        current_user_object_id = convert_to_pydantic_object_id(current_user_id)
        study_room_object_id = convert_to_pydantic_object_id(study_room_id)

        study_room = await self.get_study_room_or_404(study_room_object_id)
        self.ensure_study_room_is_active(study_room)

        is_participant_in_other_room = await StudyRoom.find_one(
            {
                "participants.user_id": current_user_object_id, 
                "is_active": True,
                "_id": {"$ne": study_room_object_id}  
            }
        )


        if is_participant_in_other_room:
            raise HTTPException(
                status_code=403, 
                detail="You are already a participant in another study room"
            )
    
        if self.is_user_participant(current_user_object_id, study_room):
            raise HTTPException(status_code=403, detail="You are already participant of this study room")
        
        study_room.participants.append(
            Participant(
                user_id=current_user_id,
                is_owner=False,
                is_active=True,
                permission=Permission.can_view,
            )
        )
        await study_room.save()



    async def remove_participant(self, current_user_id: str, study_room_id: str, participant_id: str):
        validate_object_id(current_user_id)
        validate_object_id(study_room_id)
        validate_object_id(participant_id)

        current_user_object_id = convert_to_pydantic_object_id(current_user_id)
        study_room_object_id = convert_to_pydantic_object_id(study_room_id)
        participant_object_id = convert_to_pydantic_object_id(participant_id)

        study_room = await self.get_study_room_or_404(study_room_object_id)

        self.ensure_study_room_is_active(study_room)
        self.ensure_user_is_participant(current_user_object_id, study_room)
        self.ensure_user_is_participant(participant_object_id, study_room)

        participant = self.find_participant(study_room, participant_object_id)
        current_user_participant = self.find_participant(study_room, current_user_object_id)

        if not (
            current_user_participant.is_owner or current_user_object_id == participant_id
        ):
            raise HTTPException(
                status_code=403,
                detail="Only the owner or the participant themselves can remove the participant",
            )

        participant.is_active = False
        await study_room.save()


    async def update_participant_permission(self, current_user_id: str, study_room_id: str, participant_id: str, permission: str):
        validate_object_id(current_user_id)
        validate_object_id(study_room_id)
        validate_object_id(participant_id)

        if permission not in Permission.__members__.values():
            raise HTTPException(status_code=400, detail="Invalid permission")

        current_user_object_id = convert_to_pydantic_object_id(current_user_id)
        participant_object_id = convert_to_pydantic_object_id(participant_id)
        study_room_object_id = convert_to_pydantic_object_id(study_room_id)

        study_room = await self.get_study_room_or_404(study_room_object_id)

        self.ensure_study_room_is_active(study_room)
        self.ensure_user_is_participant(current_user_object_id, study_room)
        self.ensure_user_is_owner(current_user_object_id, study_room)

        participant = self.find_participant(study_room, participant_object_id)

        if participant.permission == permission:
            raise HTTPException(status_code=400, detail="The new permission is the same as the current permission")

        participant.permission = permission
        await study_room.save()

