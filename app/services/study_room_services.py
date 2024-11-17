from datetime import datetime
from beanie import PydanticObjectId
from fastapi import HTTPException
from app.models.study_room import StudyRoom
from app.schemas import Participant, StudyRoomCreate, StudyRoomInfoUpdate, StudyRoomOut
from app.utils import convert_to_pydantic_object_id, convert_to_str, validate_object_id
from fastapi import status
from typing import List

class StudyRoomServices:
    



    async def is_user_in_active_room(self, user_id: PydanticObjectId) -> bool:
        active_rooms = await StudyRoom.find(StudyRoom.is_active == True).to_list()

        for room in active_rooms:
            if room.owner_id == user_id:
                return True
            # Check if any participant in the list has the given participant_id
            if len(room.active_participants) > 0:
                if any(participant["participant_id"] == user_id for participant in room.active_participants):
                    return True
        return False


    async def is_user_owner(self, user_id: PydanticObjectId, study_room_id: PydanticObjectId) -> bool:
        study_room = await StudyRoom.get(study_room_id)
        if study_room:
            return study_room.owner_id == user_id
        return False
    

    async def is_user_allowed_to_edit_study_room(self, user_id: PydanticObjectId, study_room_id: PydanticObjectId) -> bool:
       
        study_room= await StudyRoom.get(study_room_id)
        if not study_room.is_active:
            return False
        if study_room.owner_id==user_id:
            return True
        
        if len(study_room.active_participants)>0:
            if any(participant["participant_id"] == user_id and participant.get("can_edit") for participant in study_room.active_participants):
                return True
            
        return False

    
    async def checkStudyRoom(self,study_room:StudyRoom | None):
        if not study_room:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study room not found."
            )
        
        if not study_room.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot perform actions on an inactive study room."
            )


    ## Study Room Operations


    async def create_study_room(self,current_user_id:str,study_room_info:StudyRoomCreate):
        validate_object_id(current_user_id)
        current_user_object_id=convert_to_pydantic_object_id(current_user_id)

        is_in_active_study_room=await self.is_user_in_active_room(current_user_object_id)
        if is_in_active_study_room:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are already in a study room"
            )

        study_room=StudyRoom(
            name=study_room_info.name,
            description=study_room_info.description,
            owner_id=current_user_object_id,
            markdown_content=''
        )
        await study_room.insert()

   
    async def end_study_room(self, current_user_id: str, study_room_id: str):
        validate_object_id(current_user_id)
        current_user_object_id = convert_to_pydantic_object_id(current_user_id)

        validate_object_id(study_room_id)
        study_room_object_id = convert_to_pydantic_object_id(study_room_id)

        study_room = await StudyRoom.get(study_room_object_id)
        await self.checkStudyRoom(study_room)

        is_owner = await self.is_user_owner(current_user_object_id, study_room_object_id)
        if not is_owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to end this study room."
            )

        if len(study_room.active_participants) > 0:
            study_room.former_participants.extend(
                [participant['participant_id'] for participant in study_room.active_participants]
            )

        # Clear the active participants and deactivate the study room
        study_room.active_participants = []
        study_room.is_active = False
        await study_room.save()




    async def transfer_study_room_ownership(
        self, current_user_id: str, new_owner_id: str, study_room_id: str
    ) -> dict:
        validate_object_id(current_user_id)
        current_user_object_id = convert_to_pydantic_object_id(current_user_id)

        validate_object_id(new_owner_id)
        new_owner_object_id = convert_to_pydantic_object_id(new_owner_id)

        validate_object_id(study_room_id)
        study_room_object_id = convert_to_pydantic_object_id(study_room_id)

        study_room = await StudyRoom.get(study_room_object_id)
        self.checkStudyRoom(study_room)

        if study_room.owner_id != current_user_object_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to transfer ownership."
            )
        

        if not any(
            participant["participant_id"] == new_owner_object_id
            for participant in study_room.active_participants
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New owner must be an active participant of the study room."
            )
        
        updated_participants=[]
        if len(study_room.active_participants)>0:
            updated_participants = [
                participant for participant in study_room.active_participants
                if participant['participant_id'] != new_owner_object_id
            ]

        updated_participants.append({"participant_id":current_user_object_id,"can_edit":False})
        study_room.owner_id = new_owner_object_id
        study_room.active_participants=updated_participants
        await study_room.save()

        
    async def update_study_room_info(self,current_user_id:str,study_room_id:str,study_room_info:StudyRoomInfoUpdate):
        validate_object_id(current_user_id)
        current_user_object_id=convert_to_pydantic_object_id(current_user_id)

        validate_object_id(study_room_id)
        study_room_object_id=convert_to_pydantic_object_id(study_room_id)

        study_room = await StudyRoom.get(study_room_object_id)
        await self.checkStudyRoom(study_room)

        is_owner=await self.is_user_owner(current_user_object_id,study_room_object_id)
        if not is_owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to update info of this study room."
            )

        if study_room_info.name is not None:
            study_room.name = study_room_info.name
        if study_room_info.description is not None:
            study_room.description = study_room_info.description
        study_room.last_modified = datetime.now()

        await study_room.save()
     

    async def update_study_room_markdown_content(self,current_user_id:str,study_room_id:str,markdown_data:str):
        validate_object_id(current_user_id)
        current_user_object_id=convert_to_pydantic_object_id(current_user_id)

        validate_object_id(study_room_id)
        study_room_object_id=convert_to_pydantic_object_id(study_room_id)


        study_room = await StudyRoom.get(study_room_object_id)
        await self.checkStudyRoom(study_room)
    
        is_owner=await self.is_user_allowed_to_edit_study_room(current_user_object_id,study_room_object_id)
        if not is_owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to edit."
            )
        
        study_room.markdown_content=markdown_data
        study_room.last_modified = datetime.now()
        await study_room.save()


    async def get_study_rooms_owned_by_user(self, current_user_id: str) :
        validate_object_id(current_user_id)
        current_user_object_id = convert_to_pydantic_object_id(current_user_id)

        study_rooms = await StudyRoom.find(
            StudyRoom.owner_id == current_user_object_id
        ).to_list()

        study_rooms_out = []
        for study_room in study_rooms:
            study_room_dict = await self.get_study_room(convert_to_str(study_room.id))
            print(study_room_dict)
            study_rooms_out.append(study_room_dict)

        return study_rooms_out


    async def get_study_rooms_participated_by_user(self, current_user_id: str) :
        validate_object_id(current_user_id)
        current_user_object_id = convert_to_pydantic_object_id(current_user_id)

        study_rooms = await StudyRoom.find(
            {"former_participants": {"$in": [current_user_object_id]}}
        ).to_list()
        
        study_rooms_out = []
        for study_room in study_rooms:
            study_room_dict = await self.get_study_room(convert_to_str(study_room.id))
            study_rooms_out.append(study_room_dict)

        return study_rooms_out


    async def get_study_room(self, study_room_id: str):
        validate_object_id(study_room_id)
        study_room_object_id = convert_to_pydantic_object_id(study_room_id)

        study_room = await StudyRoom.get(study_room_object_id)
        
        if not study_room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Study room not found."
            )

        active_participants = []
        if len(study_room.active_participants) > 0:
            active_participants = [
                {"participant_id": str(participant["participant_id"]), "can_edit": participant["can_edit"]}
                for participant in study_room.active_participants
            ]

        study_room_out = StudyRoomOut(
            id=str(study_room_object_id), 
            name=study_room.name,
            description=study_room.description,
            owner_id=str(study_room.owner_id),  
            active_participants=active_participants,
            former_participants=[str(participant) for participant in study_room.former_participants],
            created_at=study_room.created_at,
            is_active=study_room.is_active,
            markdown_content=study_room.markdown_content,
            last_modified=study_room.last_modified
        )
        return study_room_out


    ## Participant Operations


    async def get_study_room_participants(self, current_user_id: str, study_room_id: str) -> dict:
        validate_object_id(current_user_id)
        current_user_object_id = convert_to_pydantic_object_id(current_user_id)

        validate_object_id(study_room_id)
        study_room_object_id = convert_to_pydantic_object_id(study_room_id)

        study_room = await StudyRoom.get(study_room_object_id)
        if not study_room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Study room not found."
            )

        if study_room.owner_id != current_user_object_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view participants of this study room."
            )

        return {
            "active_participants": [
                {"participant_id": convert_to_str(participant["participant_id"]), "can_edit": participant["can_edit"]}
                for participant in study_room.active_participants
            ],
            "former_participants": [convert_to_str(participant) for participant in study_room.former_participants]
    }


    async def join_study_room(self,current_user_id:str,study_room_id:str):
        validate_object_id(current_user_id)
        current_user_object_id=convert_to_pydantic_object_id(current_user_id)

        validate_object_id(study_room_id)
        study_room_object_id=convert_to_pydantic_object_id(study_room_id)

        study_room = await StudyRoom.get(study_room_object_id)
        await self.checkStudyRoom(study_room)
        
        if study_room.owner_id==current_user_object_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is owner of the study room."
            )
        
        for participant in study_room.active_participants:
            if participant['participant_id'] == current_user_object_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User is already an active participant in this study room."
                )

        for participant in study_room.former_participants:
            if participant==current_user_object_id:
                study_room.former_participants.remove(current_user_object_id)
                break

        study_room.active_participants.append({"participant_id":current_user_object_id, "can_edit":False})
        await study_room.save()


    async def remove_user_from_study_room(self,user_id:str,current_user_id:str,study_room_id:str):
        validate_object_id(user_id)
        user_object_id=convert_to_pydantic_object_id(user_id)

        validate_object_id(current_user_id)
        current_user_object_id=convert_to_pydantic_object_id(current_user_id)

        validate_object_id(study_room_id)
        study_room_object_id=convert_to_pydantic_object_id(study_room_id)

        study_room = await StudyRoom.get(study_room_object_id)
        await self.checkStudyRoom(study_room)
        
        if study_room.owner_id != current_user_object_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the owner can remove other users."
            )       
        
        updated_participants=[]
        if len(study_room.active_participants)>0:
            updated_participants = [
                participant for participant in study_room.active_participants
                if participant['participant_id'] != user_object_id
            ]

        if len(updated_participants) == len(study_room.active_participants):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User is not an active participant in the study room."
            )

        study_room.active_participants = updated_participants
        study_room.former_participants.append(user_object_id)
        await study_room.save()

      
    async def leave_study_room(self,current_user_id:str,study_room_id:str):
        validate_object_id(current_user_id)
        current_user_object_id=convert_to_pydantic_object_id(current_user_id)

        validate_object_id(study_room_id)
        study_room_object_id=convert_to_pydantic_object_id(study_room_id)
            
        study_room = await StudyRoom.get(study_room_object_id)
        await self.checkStudyRoom(study_room)
        
        if study_room.owner_id != current_user_object_id:
            updated_participants = [
                participant for participant in study_room.active_participants
                if participant['participant_id'] != current_user_object_id
            ]

            if len(updated_participants) == len(study_room.active_participants):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User is not an active participant in the study room."
                )

            study_room.active_participants = updated_participants
            study_room.former_participants.append(current_user_object_id)
        else:
            study_room.is_active=False
            if len(study_room.active_participants) > 0:
                study_room.former_participants.extend(
                    [participant['participant_id'] for participant in study_room.active_participants]
                )

            study_room.active_participants = []

        await study_room.save()
    

    ## Permission Management


    async def grant_edit_permission(self,user_id:str,current_user_id:str,study_room_id:str):
        validate_object_id(user_id)
        user_object_id=convert_to_pydantic_object_id(user_id)

        validate_object_id(current_user_id)
        current_user_object_id=convert_to_pydantic_object_id(current_user_id)

        validate_object_id(study_room_id)
        study_room_object_id=convert_to_pydantic_object_id(study_room_id)

        study_room = await StudyRoom.get(study_room_object_id)
        await self.checkStudyRoom(study_room)
        
        if current_user_object_id==user_object_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Owner already had an edit permission."
            ) 
        
        if study_room.owner_id != current_user_object_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the owner can grant edit permissions."
            )       

        is_active=False

        for participant in study_room.active_participants:
            if participant['participant_id']==user_object_id:
                is_active=True
                if participant['can_edit'] == True:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="User already have edit permission in this study room."
                    )
                else:
                    participant['can_edit'] = True
                    await study_room.save()

        if not is_active:
            raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User need to be an active participant in study room."
                )
       

    async def revoke_edit_permission(self, user_id: str, current_user_id: str, study_room_id: str):
        validate_object_id(user_id)
        user_object_id = convert_to_pydantic_object_id(user_id)

        validate_object_id(current_user_id)
        current_user_object_id = convert_to_pydantic_object_id(current_user_id)

        validate_object_id(study_room_id)
        study_room_object_id = convert_to_pydantic_object_id(study_room_id)

        study_room = await StudyRoom.get(study_room_object_id)
        await self.checkStudyRoom(study_room)

        if study_room.owner_id != current_user_object_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the owner can revoke edit permissions."
            )

        is_active = False

        for participant in study_room.active_participants:
            if participant['participant_id'] == user_object_id:
                is_active = True
                if participant['can_edit'] == False:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="User does not have edit permissions in this study room."
                    )
                else:
                    participant['can_edit'] = False
                    await study_room.save()

        # not reach till this is user is an active member
        if not is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User needs to be an active participant in the study room."
            )
