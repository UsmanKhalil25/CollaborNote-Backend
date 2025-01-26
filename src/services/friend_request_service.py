from fastapi import HTTPException, status
from datetime import datetime
from typing import List, Optional

from src.documents.friend_request_document import FriendRequest, FriendRequestStatus
from src.documents.user_document import User
from src.services.user_service import UserService
from src.schemas.friend_request import FriendRequestReceived
from src.schemas.user import UserInfo
from src.repositories.friend_request_repository import FriendRequestRepository
from src.utils import validate_object_id, convert_to_pydantic_object_id, convert_to_str


class FriendRequestService:

    def __init__(self):
        self.user_service = UserService()
        self.friend_request_repository = FriendRequestRepository()

    async def get_valid_friend_request(self, friend_request_id: str) -> FriendRequest:
        """Fetch and validate a FriendRequest by ID."""

        validate_object_id(friend_request_id)
        friend_request_object_id = convert_to_pydantic_object_id(friend_request_id)

        friend_request = await self.friend_request_repository.get_by_id(
            friend_request_object_id
        )
        if not friend_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"FriendRequest with ID {friend_request_id} not found",
            )
        return friend_request

    async def get_received_requests(
        self, status: Optional[str], user_id: str
    ) -> List[dict]:
        """Retrieve a list of received friend requests for a given user with optional status filtering."""

        user = await self.user_service.get_valid_user(user_id=user_id)

        upper_case_status = "PENDING" if not status else status.upper()

        valid_state = FriendRequestStatus.__members__.get(upper_case_status)
        if not valid_state:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status"
            )

        FRIEND_REQUEST_RECEIVED_QUERY = {
            "receiver_id": user.id,
            "status": upper_case_status.lower(),
        }

        received_requests = await FriendRequestRepository.search_by_query(
            FRIEND_REQUEST_RECEIVED_QUERY
        )

        requests_with_senders = []
        for friend_request in received_requests:
            sender_user = await User.get(friend_request.sender_id)
            if sender_user:
                friend_request_data = FriendRequestReceived(
                    id=str(friend_request.id),
                    created_at=friend_request.created_at,
                    updated_at=friend_request.updated_at,
                    sender_id=str(friend_request.sender_id),
                    receiver_id=str(friend_request.receiver_id),
                    status=friend_request.status.value,
                    sender_info=UserInfo(
                        id=str(sender_user.id),
                        email=sender_user.email,
                        first_name=sender_user.first_name,
                        last_name=sender_user.last_name,
                    ),
                )
                requests_with_senders.append(friend_request_data)

        return requests_with_senders

    async def send_friend_request(self, from_user_id: str, to_user_id: str):
        """Send a friend request from one user to another."""

        from_user = await self.user_service.get_valid_user(user_id=from_user_id)
        to_user = await self.user_service.get_valid_user(user_id=to_user_id)

        if self.user_service.are_users_friends(
            from_user, to_user
        ) or self.user_service.are_users_friends(to_user, from_user):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are already friends with this user",
            )

        existing_request = await FriendRequest.find_one(
            FriendRequest.sender_id == from_user.id,
            FriendRequest.receiver_id == to_user.id,
            FriendRequest.status == FriendRequestStatus.PENDING,
        )

        if existing_request:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A friend request already exists between these users",
            )

        existing_request = await FriendRequest.find_one(
            FriendRequest.receiver_id == from_user.id,
            FriendRequest.sender_id == to_user.id,
            FriendRequest.status == FriendRequestStatus.PENDING,
        )

        if existing_request:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A friend request already exists between these users",
            )

        friend_request = FriendRequest(
            sender_id=from_user.id,
            receiver_id=to_user.id,
            status=FriendRequestStatus.PENDING,
        )

        await friend_request.insert()

        from_user.friend_requests_sent.append(friend_request.id)
        to_user.friend_requests_received.append(friend_request.id)

        await from_user.save()
        await to_user.save()

        return friend_request

    async def update_request_status(
        self, user_id: str, request_id: str, request_status: str
    ):
        """Update the status of a friend request."""
        user = await self.user_service.get_valid_user(user_id)
        friend_request = await self.get_valid_friend_request(request_id)

        upper_case_status = request_status.upper()
        valid_state = FriendRequestStatus.__members__.get(upper_case_status)
        if not valid_state:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status"
            )

        if friend_request.id not in user.friend_requests_received:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to update this friend request",
            )

        if friend_request.status == valid_state:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The request is already in the desired state",
            )

        if (
            friend_request.status
            in {FriendRequestStatus.ACCEPTED, FriendRequestStatus.REJECTED}
            and upper_case_status == "PENDING"
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot revert to pending from accepted or rejected",
            )

        if (
            friend_request.status == FriendRequestStatus.REJECTED
            and upper_case_status == "ACCEPTED"
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot accept a rejected friend request",
            )

        if (
            friend_request.status == FriendRequestStatus.ACCEPTED
            and upper_case_status == "REJECTED"
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot reject an accepted friend request",
            )

        friend_request.status = valid_state
        friend_request.updated_at = datetime.now()

        if valid_state == FriendRequestStatus.ACCEPTED:
            existing_request = await FriendRequest.find_one(
                FriendRequest.receiver_id == friend_request.sender_id,
                FriendRequest.sender_id == friend_request.receiver_id,
                FriendRequest.status == FriendRequestStatus.PENDING,
            )

            if existing_request:
                await existing_request.delete()

            friend = await self.user_service.get_valid_user(
                user_id=convert_to_str(friend_request.sender_id)
            )
            await self.user_service.update_friendship(user, friend, add=True)

        await friend_request.save()

        return friend_request
