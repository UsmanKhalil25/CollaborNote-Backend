from fastapi import APIRouter, Depends, status
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

@router.get("/{user_id}")
async def get_received_friend_requests(
    user_id: str,
    friend_request_controller: FriendRequestController = Depends(get_friend_request_controller),
    user_service: UserService = Depends(get_user_service)

):
    return await friend_request_controller.get_received_requests(user_id, user_service)


@router.post("/{from_user_id}/send/{to_user_id}", status_code=status.HTTP_201_CREATED)
async def send_friend_request(
    from_user_id: str,
    to_user_id: str,
    friend_request_controller: FriendRequestController = Depends(get_friend_request_controller),
    user_service: UserService = Depends(get_user_service)

):
    return await friend_request_controller.send_friend_request(from_user_id, to_user_id, user_service)
    


@router.patch("/{request_id}/status")
async def update_friend_request_status(
    request_id: str,
    new_status: str,
    friend_request_controller: FriendRequestController = Depends(get_friend_request_controller),
    user_service: UserService = Depends(get_user_service)

):
    return await friend_request_controller.update_request_status(request_id, new_status, user_service)
