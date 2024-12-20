from typing import Optional
from src.services.user_service import UserService
from src.utils import create_response
from src.constants import RESPONSE_STATUS_SUCCESS
from src.services.friend_request_service import FriendRequestService


class FriendRequestController:
    def __init__(self):
        self.friend_request_service = FriendRequestService()

    async def get_received_requests(
        self, user_id: str, status: Optional[str], user_service: UserService
    ):
        friend_request = await self.friend_request_service.get_received_requests(
            user_id, status, user_service
        )
        return create_response(
            RESPONSE_STATUS_SUCCESS,
            "Friend requests fetched successfully",
            data={"friend_requests": friend_request},
        )

    async def send_friend_request(
        self, from_user_id: str, to_user_id: str, user_service: UserService
    ):
        await self.friend_request_service.send_friend_request(
            from_user_id, to_user_id, user_service
        )
        return create_response(
            RESPONSE_STATUS_SUCCESS, "Friend request sent successfully"
        )

    async def update_request_status(
        self, user_id: str, request_id: str, status: str, user_service: UserService
    ):
        await self.friend_request_service.update_request_status(
            user_id, request_id, status, user_service
        )
        return create_response(RESPONSE_STATUS_SUCCESS, "Friend request status updated")
