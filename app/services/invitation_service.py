from fastapi import HTTPException

from app.schemas.invitation import InvitationCreate, InvitationStatus

from app.models.invitation import Invitation

from app.services.study_room_service import StudyRoomService

from app.utils import validate_object_id, convert_to_pydantic_object_id


class InvitationService:
    
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
            Invitation.study_room_id == invitation.study_room_id,
            Invitation.invited_user_id == invitation.invited_user_id,
            Invitation.inviter_user_id == current_user_id,
            Invitation.status == InvitationStatus.PENDING
        )

        if existing_invitation:
            raise HTTPException(
                status_code=403, 
                detail="An invitation for this user already exists."
            )

        new_invitation = Invitation(
            study_room_id = invitation.study_room_id,
            invited_user_id = invitation.invited_user_id,
            inviter_user_id = current_user_id,
        )

        await new_invitation.insert()


        


        

        





    