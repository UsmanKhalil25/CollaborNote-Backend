from fastapi import APIRouter, status, Depends

from app.auth.token_manager import TokenManager
from app.controllers.invitation_controller import InvitationController
from app.services.study_room_service import StudyRoomService

from app.schemas.token import TokenData
from app.schemas.invitation import InvitationCreate
router = APIRouter(
    prefix="/invitations",
    tags=["Invitation"]
)

def get_invitation_controller() -> InvitationController:
    return InvitationController()

def get_study_room_service() -> StudyRoomService:
    return StudyRoomService()

def get_token_manager()->TokenManager:
    return TokenManager()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_invitation(
    invitation: InvitationCreate,
    token: TokenData = Depends(get_token_manager().get_current_user),
    invitation_controller: InvitationController = Depends(get_invitation_controller),
    study_room_service: StudyRoomService = Depends(get_study_room_service)

):
    user_id = token.id
    return await invitation_controller.create_invitation(user_id, invitation, study_room_service)