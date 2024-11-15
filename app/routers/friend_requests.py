from fastapi import APIRouter, Depends, status
from app.schemas import TokenData
from app.auth.token_manager import TokenManager
from app.services.user_service import UserService
from app.controllers.friend_request_controller import FriendRequestController

router = APIRouter(
    prefix="/friend-requests",
    tags=["Friend Requests"]
)

def get_friend_request_controller() -> FriendRequestController:
    return FriendRequestController()

def get_user_service() -> UserService:
    return UserService()

def get_token_manager() -> TokenManager:
    return TokenManager()

@router.get("")
async def get_received_friend_requests(
    token: TokenData = Depends(get_token_manager().get_current_user),
    friend_request_controller: FriendRequestController = Depends(get_friend_request_controller),
    user_service: UserService = Depends(get_user_service)
):
    user_id = token.id
    return await friend_request_controller.get_received_requests(user_id, user_service)

@router.post("/send/{to_user_id}", status_code=status.HTTP_201_CREATED)
async def send_friend_request(
    to_user_id: str,
    token: TokenData = Depends(get_token_manager().get_current_user),
    friend_request_controller: FriendRequestController = Depends(get_friend_request_controller),
    user_service: UserService = Depends(get_user_service)
):
    from_user_id = token.id
    return await friend_request_controller.send_friend_request(from_user_id, to_user_id, user_service)

@router.patch("/{request_id}/status")
async def update_friend_request_status(
    request_id: str,
    new_status: str,
    token: TokenData = Depends(get_token_manager().get_current_user),
    friend_request_controller: FriendRequestController = Depends(get_friend_request_controller),
    user_service: UserService = Depends(get_user_service)

):
    user_id = token.id
    return await friend_request_controller.update_request_status(user_id, request_id, new_status, user_service)