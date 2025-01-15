from typing import Optional
from src.services.user_service import UserService
from src.utils import create_response
from src.constants import RESPONSE_STATUS_SUCCESS
from src.schemas.token import TokenData
from src.services.friend_request_service import FriendRequestService


class FriendRequestController:
    """Controller for handling friend request operations."""

    def __init__(self):
        self.friend_request_service = FriendRequestService()

    async def get_received_requests(self, status: Optional[str], token: TokenData):
        """Fetch received friend requests for the authenticated user."""

        user_id = token.user_id
        friend_request = await self.friend_request_service.get_received_requests(
            status=status, user_id=user_id
        )

        return create_response(
            RESPONSE_STATUS_SUCCESS,
            "Friend requests fetched successfully",
            data={"friend_requests": friend_request},
        )

    async def send_friend_request(self, token: TokenData, to_user_id: str):
        """Send a friend request to another user."""

        user_id = token.user_id
        await self.friend_request_service.send_friend_request(
            from_user_id=user_id, to_user_id=to_user_id
        )
        return create_response(
            RESPONSE_STATUS_SUCCESS, "Friend request sent successfully"
        )

    async def update_request_status(
        self, token: TokenData, request_id: str, request_status: str
    ):
        """Update the status of a friend request."""

        user_id = token.user_id
        await self.friend_request_service.update_request_status(
            user_id=user_id, request_id=request_id, request_status=request_status
        )
        return create_response(RESPONSE_STATUS_SUCCESS, "Friend request status updated")
