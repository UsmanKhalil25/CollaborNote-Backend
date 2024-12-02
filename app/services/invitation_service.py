from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException
from beanie import PydanticObjectId

from app.schemas.invitation import InvitationCreate, InvitationStatus, InvitationListOut
from app.schemas.user import UserInfo

from app.models.invitation import Invitation
from app.models.study_room import StudyRoom
from app.models.user import User

from app.schemas.study_room import StudyRoomListingOut
from app.services.study_room_service import StudyRoomService
from app.services.user_service import UserService

from app.utils import validate_object_id, convert_to_pydantic_object_id, validate_enum_status


class InvitationService:

    @staticmethod
    async def get_invitation_or_404(invitation_id: PydanticObjectId) -> Invitation:

            invitation = await Invitation.get(invitation_id)
            if not invitation:
                raise HTTPException(status_code=404, detail="Invitation not found")
            return invitation
    
    @staticmethod
    def validate_invitation_status(status: Optional[str]):
        upper_case_status = None
        if status:
            upper_case_status = status.upper()
            valid_state = InvitationStatus.__members__.get(upper_case_status)
            if not valid_state:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid status"
                )
            
    
    async def get_received_invitations(self, current_user_id: str, study_room_service: StudyRoomService, user_service: UserService) -> List[InvitationListOut]:
        validate_object_id(current_user_id)

        current_user_object_id = PydanticObjectId(current_user_id)

        invitations = await Invitation.find(
            Invitation.invited_user_id == current_user_object_id,
            Invitation.status == InvitationStatus.PENDING
        ).to_list()

        invitation_list = []
        for invitation in invitations:
            inviter_user = await user_service.get_user_by_id(invitation.inviter_user_id)
            inviter_user_info = UserInfo(
                email = inviter_user.email,
                first_name = inviter_user.first_name,
                last_name = inviter_user.last_name 
            )
            
            study_room = await study_room_service.get_study_room_or_404(invitation.study_room_id)

            participants_out = [
                await study_room_service.map_participant_to_out(participant) for participant in study_room.participants if participant
            ]

            study_room_info = StudyRoomListingOut(
                id=str(study_room.id),
                name=study_room.name,
                description=study_room.description,
                created_at=study_room.created_at,
                participants=participants_out,
            )

            invitation_list.append(
                InvitationListOut(
                    id=str(invitation.id),
                    study_room_id=str(invitation.study_room_id),
                    invited_user_id=str(invitation.invited_user_id),
                    inviter_user_id=str(invitation.inviter_user_id),
                    status=invitation.status,
                    created_at=invitation.created_at,
                    responded_at=invitation.responded_at,
                    inviter_user_info=inviter_user_info,
                    study_room_info=study_room_info,
                )
            )

        return invitation_list


    async def create_invitation(self, current_user_id: str, invitation: InvitationCreate, study_room_service: StudyRoomService):
        validate_object_id(current_user_id)
        validate_object_id(invitation.study_room_id)
        validate_object_id(invitation.invited_user_id)

        if current_user_id == invitation.invited_user_id:
            raise HTTPException(
                status_code=400, detail="You cannot invite yourself to the study room."
            )

        current_user_object_id = convert_to_pydantic_object_id(current_user_id)
        study_room_object_id = convert_to_pydantic_object_id(invitation.study_room_id)
        invited_user_object_id = convert_to_pydantic_object_id(invitation.invited_user_id)

        study_room = await study_room_service.get_study_room_or_404(study_room_object_id)

        current_user_participant = study_room_service.find_participant_by_user_id(current_user_object_id, study_room)
        if not current_user_participant:
            raise HTTPException(
                status_code=403, detail="You are not a participant in the study room."
            )

        invited_user_participant = study_room_service.find_participant_by_user_id(invited_user_object_id, study_room)
        if invited_user_participant:
            raise HTTPException(
                status_code=403, detail="Invited user is already a participant in the study room."
            )

        existing_invitation = await Invitation.find_one(
            Invitation.study_room_id == study_room_object_id,
            Invitation.invited_user_id == invited_user_object_id,
            Invitation.inviter_user_id == current_user_object_id,
            Invitation.status == InvitationStatus.PENDING
        )

        if existing_invitation:
            raise HTTPException(
                status_code=403, 
                detail="An invitation for this user already exists."
            )

        new_invitation = Invitation(
            study_room_id = study_room_object_id,
            invited_user_id = invited_user_object_id,
            inviter_user_id = current_user_object_id,
        )

        await new_invitation.insert()

    async def update_invitation_status(self, current_user_id: str, invitation_id: str, new_status: str):
        validate_object_id(current_user_id)
        validate_object_id(invitation_id)

        current_user_object_id = convert_to_pydantic_object_id(current_user_id)
        invitation_object_id = convert_to_pydantic_object_id(invitation_id)

        invitation = await self.get_invitation_or_404(invitation_object_id)

        if invitation.invited_user_id != current_user_object_id:
            raise HTTPException(
                status_code=403, detail="You cannot update the invitation status of other users."
            )

        upper_case_status = new_status.upper()

        validate_enum_status(InvitationStatus, upper_case_status, "Invalid invitation status")

        if invitation.status == upper_case_status:
            raise HTTPException(
                status_code=400, detail="The new status is the same as the current status."
            )

        if invitation.status in {InvitationStatus.ACCEPTED.name, InvitationStatus.REJECTED.name}:
            raise HTTPException(
                status_code=400, detail="You cannot update an invitation that is already accepted or rejected."
            )

        invitation.status = upper_case_status
        invitation.responded_at = datetime.now()
        await invitation.save()
            




        


        

        





    