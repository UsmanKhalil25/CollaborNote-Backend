from fastapi import APIRouter, status, Depends

from src.services.token_manager import TokenManager
from src.controllers.invitation_controller import InvitationController
from src.services.study_room_service import StudyRoomService
from src.services.user_service import UserService

from src.schemas.token import TokenData
from src.schemas.invitation import InvitationCreate

router = APIRouter(prefix="/invitations", tags=["Invitation"])


def get_invitation_controller() -> InvitationController:
    return InvitationController()


def get_study_room_service() -> StudyRoomService:
    return StudyRoomService()


def get_user_service() -> UserService:
    return UserService()


def get_token_manager() -> TokenManager:
    return TokenManager()


@router.get("")
async def get_received_invitations(
    token: TokenData = Depends(get_token_manager().verify_token),
    invitation_controller: InvitationController = Depends(get_invitation_controller),
    study_room_service: StudyRoomService = Depends(get_study_room_service),
    user_service: UserService = Depends(get_user_service),
):
    current_user_id = token.id
    return await invitation_controller.get_received_invitations(
        current_user_id, study_room_service, user_service
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_invitation(
    invitation: InvitationCreate,
    token: TokenData = Depends(get_token_manager().verify_token),
    invitation_controller: InvitationController = Depends(get_invitation_controller),
    study_room_service: StudyRoomService = Depends(get_study_room_service),
):
    current_user_id = token.id
    return await invitation_controller.create_invitation(
        current_user_id, invitation, study_room_service
    )


@router.patch("/{invitation_id}/status")
async def create_invitation(
    invitation_id: str,
    new_status: str,
    token: TokenData = Depends(get_token_manager().verify_token),
    invitation_controller: InvitationController = Depends(get_invitation_controller),
):
    current_user_id = token.id
    return await invitation_controller.update_invitation_status(
        current_user_id, invitation_id, new_status
    )
