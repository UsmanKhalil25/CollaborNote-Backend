from fastapi import APIRouter, Depends, status
from typing import Optional

from src.schemas.token import TokenData
from src.services.token_service import TokenService
from src.controllers.friend_request_controller import FriendRequestController

router = APIRouter(prefix="/friend-requests", tags=["Friend Requests"])


def get_friend_request_controller() -> FriendRequestController:
    """Provides a FriendRequestController instance."""

    return FriendRequestController()


def get_token_service() -> TokenService:
    """Provides a TokenService instance."""

    return TokenService()


@router.get("")
async def get_received_friend_requests(
    status: Optional[str] = None,
    token: TokenData = Depends(get_token_service().validate_access_token),
    friend_request_controller: FriendRequestController = Depends(
        get_friend_request_controller
    ),
):
    return await friend_request_controller.get_received_requests(status, token)


@router.post("/{to_user_id}", status_code=status.HTTP_201_CREATED)
async def send_friend_request(
    to_user_id: str,
    token: TokenData = Depends(get_token_service().validate_access_token),
    friend_request_controller: FriendRequestController = Depends(
        get_friend_request_controller
    ),
):
    return await friend_request_controller.send_friend_request(token, to_user_id)


@router.patch("/{request_id}")
async def update_friend_request_status(
    request_id: str,
    request_status: str,
    token: TokenData = Depends(get_token_service().validate_access_token),
    friend_request_controller: FriendRequestController = Depends(
        get_friend_request_controller
    ),
):
    return await friend_request_controller.update_request_status(
        token, request_id, request_status
    )
