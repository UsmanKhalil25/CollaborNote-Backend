from app.constants import RESPONSE_STATUS_SUCCESS
from app.services.invitation_service import InvitationService
from app.schemas.invitation import InvitationCreate
from app.services.study_room_service import StudyRoomService
from app.utils import create_response

class InvitationController:
    
    def __init__(self):
        self.invitation_service = InvitationService()

    async def create_invitation(self, user_id: str, invitation: InvitationCreate, study_room_service: StudyRoomService):
        await self.invitation_service.create_invitation(user_id, invitation, study_room_service)
        return create_response(RESPONSE_STATUS_SUCCESS, "Invitation created successfully")
