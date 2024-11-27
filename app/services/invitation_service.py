from typing import Optional
from fastapi import HTTPException
from beanie import PydanticObjectId

from app.schemas.invitation import InvitationCreate, InvitationStatus

from app.models.invitation import Invitation

from app.services.study_room_service import StudyRoomService

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
            
    
    async def get_received_invitations(self, current_user_id: str):
        validate_object_id(current_user_id)

        current_user_object_id = convert_to_pydantic_object_id(current_user_id)

        invitations = await Invitation.find(
            Invitation.invited_user_id == current_user_object_id,
            Invitation.status == InvitationStatus.PENDING
        )

        return invitations


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
        await invitation.save()
            




        


        

        





    