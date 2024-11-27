from app.schemas.invitation import InvitationCreate

from app.services.invitation_service import InvitationService
from app.services.study_room_service import StudyRoomService
from app.services.user_service import UserService
from app.utils import create_response
from app.constants import RESPONSE_STATUS_SUCCESS

class InvitationController:
    
    def __init__(self):
        self.invitation_service = InvitationService()

    async def get_received_invitations(self, current_user_id: str, study_room_service: StudyRoomService, user_service: UserService):
        invitations = await self.invitation_service.get_received_invitations(current_user_id, study_room_service, user_service)
        return create_response(RESPONSE_STATUS_SUCCESS, "Invitation fetched successfully", data={"invitations": invitations})

    async def create_invitation(self, current_user_id: str, invitation: InvitationCreate, study_room_service: StudyRoomService):
        await self.invitation_service.create_invitation(current_user_id, invitation, study_room_service)
        return create_response(RESPONSE_STATUS_SUCCESS, "Invitation created successfully")
    
    async def update_invitation_status(self, current_user_id: str, invitation_id: str, new_status: str):
        await self.invitation_service.update_invitation_status(current_user_id, invitation_id, new_status)
        return create_response(RESPONSE_STATUS_SUCCESS, "Invitation status updated successfully")


